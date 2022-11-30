import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import core_routes from "common/routes";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import reportWebVitals from './reportWebVitals';

// Importing the Bootstrap CSS
import 'bootstrap/dist/css/bootstrap.css';

export default function nautobot_static() {
  if (process.env.NODE_ENV === "development") {
    return "/nautobot_static";
  } else {
    return "/static";
  }
}

const router = createBrowserRouter(core_routes);

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();