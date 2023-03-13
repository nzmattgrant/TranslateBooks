import { createApp } from "vue";
import { createPinia } from "pinia";
import Popper from "vue3-popper";

import App from "./App.vue";
import router from "./router";

import "./assets/main.css";

const app = createApp(App);

app.use(createPinia());
app.use(router);
app.component("Popper", Popper);

app.mount("#app");
