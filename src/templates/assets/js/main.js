window.$ = window.jQuery = require('jquery');
import 'startbootstrap-sb-admin-2/js/sb-admin-2'
import Vue from 'vue';

import '../scss/main.scss'

window.Vue = Vue

Vue.component('create-product', require('./components/product/CreateProduct.vue').default)
console.log("loading.....")
const main = new Vue({
    el: '#app'
})