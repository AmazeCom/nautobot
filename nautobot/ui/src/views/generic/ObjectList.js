import { useParams } from "react-router-dom";
import { Text } from "@nautobot/nautobot-ui";
import { useDispatch } from "react-redux";

import { LoadingWidget } from "@components/LoadingWidget";
import ObjectListTable from "@components/ObjectListTable";
import GenericView from "@views/generic/GenericView";
import { useGetRESTAPIQuery } from "@utils/api";
import { useEffect } from "react";
import {
    updateAppCurrentContext,
    getCurrentAppContextSelector,
} from "@utils/store";
import { useSelector } from "react-redux";

export default function GenericObjectListView() {
    const { app_name, model_name } = useParams();
    const dispatch = useDispatch();
    const currentAppContext = useSelector(
        getCurrentAppContextSelector(app_name, model_name)
    );
    useEffect(() => {
        dispatch(updateAppCurrentContext(currentAppContext));
    }, [dispatch, currentAppContext]);
    // const { 0: searchParams } = useSearchParams(); // import { useSearchParams } from "react-router-dom";
    const { data: listData, isLoading: listDataLoading } = useGetRESTAPIQuery({
        app_name: app_name,
        model_name: model_name,
    });
    const { data: headerData, isLoading: headerDataLoading } =
        useGetRESTAPIQuery({
            app_name: app_name,
            model_name: model_name,
            schema: true,
        });

    // What page are we on?
    // TODO: Pagination handling should be it's own function so it's testable
    // let page_size = 50;
    // let active_page_number = 0;
    // if (searchParams.get("limit")) {
    //     list_url += `?limit=${searchParams.get("limit")}`;
    //     page_size = searchParams.get("limit");
    // }
    // if (searchParams.get("offset")) {
    //     list_url += `&offset=${searchParams.get("offset")}`;
    //     active_page_number = searchParams.get("offset") / page_size;
    // }

    if (!app_name || !model_name) {
        return (
            <GenericView>
                <LoadingWidget />
            </GenericView>
        );
    }

    if (listDataLoading || headerDataLoading) {
        return (
            <GenericView>
                <LoadingWidget name={model_name} />
            </GenericView>
        );
    }

    if (!listData || !headerData) {
        return (
            <GenericView>
                <Text>Error loading.</Text>
            </GenericView>
        );
    }

    const transformedHeader = Object.entries(headerData.schema.properties).map(
        ([key, value]) => {
            return { name: key, label: value.title };
        }
    );
    let table_name = model_name
        .split("-")
        .map((x) => (x ? x[0].toUpperCase() + x.slice(1) : ""))
        .join(" ");
    return (
        <GenericView>
            <ObjectListTable
                tableData={listData.results}
                tableHeader={transformedHeader}
                totalCount={listData.count}
                active_page_number={1}
                page_size={50}
                tableTitle={table_name}
            />
        </GenericView>
    );
}