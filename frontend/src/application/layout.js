import "../styles/index.scss";

import "@popperjs/core";
import * as bootstrap from 'bootstrap';
window.bootstrap = bootstrap;

const toasts = document.getElementsByClassName("toast");

for (let i = 0; i < toasts.length; i++) {
    const toast = new bootstrap.Toast(toasts[i]);
    toast.show();
}

const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
[...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));

function dismissAll() {
    for (let i = 0; i < toasts.length; i++) {
        const toast = bootstrap.Toast.getInstance(toasts[i]);
        toast.hide();
    }
}

window.dismissAll = dismissAll;
