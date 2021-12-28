from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from dcim.choices import *
from dcim.constants import *
from extras.utils import extras_features
from netbox.models import ChangeLoggedModel
from utilities.fields import ColorField, NaturalOrderingField
from utilities.ordering import naturalize_interface
from .device_components import (
    ConsolePort, ConsoleServerPort, DeviceBay, FrontPort, Interface, ModuleBay, PowerOutlet, PowerPort, RearPort,
)


__all__ = (
    'ConsolePortTemplate',
    'ConsoleServerPortTemplate',
    'DeviceBayTemplate',
    'FrontPortTemplate',
    'InterfaceTemplate',
    'ModuleBayTemplate',
    'PowerOutletTemplate',
    'PowerPortTemplate',
    'RearPortTemplate',
)


class ComponentTemplateModel(ChangeLoggedModel):
    device_type = models.ForeignKey(
        to='dcim.DeviceType',
        on_delete=models.CASCADE,
        related_name='%(class)ss'
    )
    name = models.CharField(
        max_length=64
    )
    _name = NaturalOrderingField(
        target_field='name',
        max_length=100,
        blank=True
    )
    label = models.CharField(
        max_length=64,
        blank=True,
        help_text="Physical label"
    )
    description = models.CharField(
        max_length=200,
        blank=True
    )

    class Meta:
        abstract = True

    def __str__(self):
        if self.label:
            return f"{self.name} ({self.label})"
        return self.name

    def instantiate(self, device):
        """
        Instantiate a new component on the specified Device.
        """
        raise NotImplementedError()

    def to_objectchange(self, action, related_object=None):
        # Annotate the parent DeviceType
        try:
            device_type = self.device_type
        except ObjectDoesNotExist:
            # The parent DeviceType has already been deleted
            device_type = None
        return super().to_objectchange(action, related_object=device_type)


class ModularComponentTemplateModel(ComponentTemplateModel):
    """
    A ComponentTemplateModel which supports optional assignment to a ModuleType.
    """
    device_type = models.ForeignKey(
        to='dcim.DeviceType',
        on_delete=models.CASCADE,
        related_name='%(class)ss',
        blank=True,
        null=True
    )
    module_type = models.ForeignKey(
        to='dcim.ModuleType',
        on_delete=models.CASCADE,
        related_name='%(class)ss',
        blank=True,
        null=True
    )

    class Meta:
        abstract = True

    def to_objectchange(self, action, related_object=None):
        # Annotate the parent DeviceType or ModuleType
        try:
            if getattr(self, 'device_type'):
                return super().to_objectchange(action, related_object=self.device_type)
        except ObjectDoesNotExist:
            pass
        try:
            if getattr(self, 'module_type'):
                return super().to_objectchange(action, related_object=self.module_type)
        except ObjectDoesNotExist:
            pass
        return super().to_objectchange(action)

    def clean(self):
        super().clean()

        # A component template must belong to a DeviceType *or* to a ModuleType
        if self.device_type and self.module_type:
            raise ValidationError(
                "A component template cannot be associated with both a device type and a module type."
            )
        if not self.device_type and not self.module_type:
            raise ValidationError(
                "A component template must be associated with either a device type or a module type."
            )

    def resolve_name(self, module):
        if module:
            return self.name.replace('{module}', module.module_bay.position)
        return self.name


@extras_features('webhooks')
class ConsolePortTemplate(ModularComponentTemplateModel):
    """
    A template for a ConsolePort to be created for a new Device.
    """
    type = models.CharField(
        max_length=50,
        choices=ConsolePortTypeChoices,
        blank=True
    )

    class Meta:
        ordering = ('device_type', 'module_type', '_name')
        unique_together = (
            ('device_type', 'name'),
            ('module_type', 'name'),
        )

    def instantiate(self, **kwargs):
        return ConsolePort(
            name=self.resolve_name(kwargs.get('module')),
            label=self.label,
            type=self.type,
            **kwargs
        )


@extras_features('webhooks')
class ConsoleServerPortTemplate(ModularComponentTemplateModel):
    """
    A template for a ConsoleServerPort to be created for a new Device.
    """
    type = models.CharField(
        max_length=50,
        choices=ConsolePortTypeChoices,
        blank=True
    )

    class Meta:
        ordering = ('device_type', 'module_type', '_name')
        unique_together = (
            ('device_type', 'name'),
            ('module_type', 'name'),
        )

    def instantiate(self, **kwargs):
        return ConsoleServerPort(
            name=self.resolve_name(kwargs.get('module')),
            label=self.label,
            type=self.type,
            **kwargs
        )


@extras_features('webhooks')
class PowerPortTemplate(ModularComponentTemplateModel):
    """
    A template for a PowerPort to be created for a new Device.
    """
    type = models.CharField(
        max_length=50,
        choices=PowerPortTypeChoices,
        blank=True
    )
    maximum_draw = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1)],
        help_text="Maximum power draw (watts)"
    )
    allocated_draw = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1)],
        help_text="Allocated power draw (watts)"
    )

    class Meta:
        ordering = ('device_type', 'module_type', '_name')
        unique_together = (
            ('device_type', 'name'),
            ('module_type', 'name'),
        )

    def instantiate(self, **kwargs):
        return PowerPort(
            name=self.resolve_name(kwargs.get('module')),
            label=self.label,
            type=self.type,
            maximum_draw=self.maximum_draw,
            allocated_draw=self.allocated_draw,
            **kwargs
        )

    def clean(self):
        super().clean()

        if self.maximum_draw is not None and self.allocated_draw is not None:
            if self.allocated_draw > self.maximum_draw:
                raise ValidationError({
                    'allocated_draw': f"Allocated draw cannot exceed the maximum draw ({self.maximum_draw}W)."
                })


@extras_features('webhooks')
class PowerOutletTemplate(ModularComponentTemplateModel):
    """
    A template for a PowerOutlet to be created for a new Device.
    """
    type = models.CharField(
        max_length=50,
        choices=PowerOutletTypeChoices,
        blank=True
    )
    power_port = models.ForeignKey(
        to='dcim.PowerPortTemplate',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='poweroutlet_templates'
    )
    feed_leg = models.CharField(
        max_length=50,
        choices=PowerOutletFeedLegChoices,
        blank=True,
        help_text="Phase (for three-phase feeds)"
    )

    class Meta:
        ordering = ('device_type', 'module_type', '_name')
        unique_together = (
            ('device_type', 'name'),
            ('module_type', 'name'),
        )

    def clean(self):
        super().clean()

        # Validate power port assignment
        if self.power_port:
            if self.device_type and self.power_port.device_type != self.device_type:
                raise ValidationError(
                    f"Parent power port ({self.power_port}) must belong to the same device type"
                )
            if self.module_type and self.power_port.module_type != self.module_type:
                raise ValidationError(
                    f"Parent power port ({self.power_port}) must belong to the same module type"
                )

    def instantiate(self, **kwargs):
        if self.power_port:
            power_port = PowerPort.objects.get(name=self.power_port.name, **kwargs)
        else:
            power_port = None
        return PowerOutlet(
            name=self.resolve_name(kwargs.get('module')),
            label=self.label,
            type=self.type,
            power_port=power_port,
            feed_leg=self.feed_leg,
            **kwargs
        )


@extras_features('webhooks')
class InterfaceTemplate(ModularComponentTemplateModel):
    """
    A template for a physical data interface on a new Device.
    """
    # Override ComponentTemplateModel._name to specify naturalize_interface function
    _name = NaturalOrderingField(
        target_field='name',
        naturalize_function=naturalize_interface,
        max_length=100,
        blank=True
    )
    type = models.CharField(
        max_length=50,
        choices=InterfaceTypeChoices
    )
    mgmt_only = models.BooleanField(
        default=False,
        verbose_name='Management only'
    )

    class Meta:
        ordering = ('device_type', 'module_type', '_name')
        unique_together = (
            ('device_type', 'name'),
            ('module_type', 'name'),
        )

    def instantiate(self, **kwargs):
        return Interface(
            name=self.resolve_name(kwargs.get('module')),
            label=self.label,
            type=self.type,
            mgmt_only=self.mgmt_only,
            **kwargs
        )


@extras_features('webhooks')
class FrontPortTemplate(ModularComponentTemplateModel):
    """
    Template for a pass-through port on the front of a new Device.
    """
    type = models.CharField(
        max_length=50,
        choices=PortTypeChoices
    )
    color = ColorField(
        blank=True
    )
    rear_port = models.ForeignKey(
        to='dcim.RearPortTemplate',
        on_delete=models.CASCADE,
        related_name='frontport_templates'
    )
    rear_port_position = models.PositiveSmallIntegerField(
        default=1,
        validators=[
            MinValueValidator(REARPORT_POSITIONS_MIN),
            MaxValueValidator(REARPORT_POSITIONS_MAX)
        ]
    )

    class Meta:
        ordering = ('device_type', 'module_type', '_name')
        unique_together = (
            ('device_type', 'name'),
            ('module_type', 'name'),
            ('rear_port', 'rear_port_position'),
        )

    def clean(self):
        super().clean()

        try:

            # Validate rear port assignment
            if self.rear_port.device_type != self.device_type:
                raise ValidationError(
                    "Rear port ({}) must belong to the same device type".format(self.rear_port)
                )

            # Validate rear port position assignment
            if self.rear_port_position > self.rear_port.positions:
                raise ValidationError(
                    "Invalid rear port position ({}); rear port {} has only {} positions".format(
                        self.rear_port_position, self.rear_port.name, self.rear_port.positions
                    )
                )

        except RearPortTemplate.DoesNotExist:
            pass

    def instantiate(self, **kwargs):
        if self.rear_port:
            rear_port = RearPort.objects.get(name=self.rear_port.name, **kwargs)
        else:
            rear_port = None
        return FrontPort(
            name=self.resolve_name(kwargs.get('module')),
            label=self.label,
            type=self.type,
            color=self.color,
            rear_port=rear_port,
            rear_port_position=self.rear_port_position,
            **kwargs
        )


@extras_features('webhooks')
class RearPortTemplate(ModularComponentTemplateModel):
    """
    Template for a pass-through port on the rear of a new Device.
    """
    type = models.CharField(
        max_length=50,
        choices=PortTypeChoices
    )
    color = ColorField(
        blank=True
    )
    positions = models.PositiveSmallIntegerField(
        default=1,
        validators=[
            MinValueValidator(REARPORT_POSITIONS_MIN),
            MaxValueValidator(REARPORT_POSITIONS_MAX)
        ]
    )

    class Meta:
        ordering = ('device_type', 'module_type', '_name')
        unique_together = (
            ('device_type', 'name'),
            ('module_type', 'name'),
        )

    def instantiate(self, **kwargs):
        return RearPort(
            name=self.resolve_name(kwargs.get('module')),
            label=self.label,
            type=self.type,
            color=self.color,
            positions=self.positions,
            **kwargs
        )


@extras_features('webhooks')
class ModuleBayTemplate(ComponentTemplateModel):
    """
    A template for a ModuleBay to be created for a new parent Device.
    """
    position = models.CharField(
        max_length=30,
        blank=True,
        help_text='Identifier to reference when renaming installed components'
    )

    class Meta:
        ordering = ('device_type', '_name')
        unique_together = ('device_type', 'name')

    def instantiate(self, device):
        return ModuleBay(
            device=device,
            name=self.name,
            label=self.label,
            position=self.position
        )


@extras_features('webhooks')
class DeviceBayTemplate(ComponentTemplateModel):
    """
    A template for a DeviceBay to be created for a new parent Device.
    """
    class Meta:
        ordering = ('device_type', '_name')
        unique_together = ('device_type', 'name')

    def instantiate(self, device):
        return DeviceBay(
            device=device,
            name=self.name,
            label=self.label
        )

    def clean(self):
        if self.device_type and self.device_type.subdevice_role != SubdeviceRoleChoices.ROLE_PARENT:
            raise ValidationError(
                f"Subdevice role of device type ({self.device_type}) must be set to \"parent\" to allow device bays."
            )