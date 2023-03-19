import "../styles/index.scss";

import "@popperjs/core";
import * as bootstrap from 'bootstrap';
window.bootstrap = bootstrap;

// const toastLiveExample = document.getElementById('liveToast');
// const toast = new bootstrap.Toast(toastLiveExample);
// toast.show();
// console.log(toast);

const toasts = document.getElementsByClassName("toast");

for (let i = 0; i < toasts.length; i++) {
    setTimeout(() => {
        const toast = new bootstrap.Toast(toasts[i]);
        toast.show();
    }, i*50);
}
