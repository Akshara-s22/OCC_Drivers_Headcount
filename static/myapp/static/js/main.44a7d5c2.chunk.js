(window.webpackJsonp=window.webpackJsonp||[]).push([[0],{17:function(e,t,a){},22:function(e,t,a){"use strict";a.r(t);var n=a(2),r=a.n(n),c=a(7),l=a.n(c),m=(a(17),a(24));var o=()=>{const[e,t]=Object(n.useState)(""),[a,c]=Object(n.useState)(""),[l,o]=Object(n.useState)([]),[i,s]=Object(n.useState)([]);return Object(n.useEffect)(()=>{e&&m.a.get("/staff-id-autocomplete/?term=".concat(e)).then(e=>o(e.data))},[e]),Object(n.useEffect)(()=>{e&&m.a.get("/get-driver-name/?staff_id=".concat(e)).then(e=>c(e.data.driver_name))},[e]),Object(n.useEffect)(()=>{a&&m.a.get("/driver-autocomplete/?term=".concat(a)).then(e=>s(e.data))},[a]),r.a.createElement("div",{className:"container form-container"},r.a.createElement("form",{method:"post"},r.a.createElement("div",{className:"form-row"},r.a.createElement("div",{className:"form-group col-md-4"},r.a.createElement("label",{htmlFor:"staff_id"},"Staff ID"),r.a.createElement("input",{type:"text",id:"staff_id",name:"staff_id",value:e,onChange:e=>t(e.target.value),list:"staff_id_list",className:"form-control"}),r.a.createElement("datalist",{id:"staff_id_list"},l.map((e,t)=>r.a.createElement("option",{key:t,value:e})))),r.a.createElement("div",{className:"form-group col-md-4"},r.a.createElement("label",{htmlFor:"driver_name"},"Driver Name"),r.a.createElement("input",{type:"text",id:"driver_name",name:"driver_name",value:a,onChange:e=>c(e.target.value),list:"driver_name_list",className:"form-control"}),r.a.createElement("datalist",{id:"driver_name_list"},i.map((e,t)=>r.a.createElement("option",{key:t,value:e})))),r.a.createElement("div",{className:"form-group col-md-4"},r.a.createElement("label",{htmlFor:"duty_card_no"},"Duty Card No"),r.a.createElement("input",{type:"text",id:"duty_card_no",name:"duty_card_no",className:"form-control"}))),r.a.createElement("button",{type:"submit",className:"btn btn-success"},"Submit")))};var i=e=>{e&&e instanceof Function&&a.e(3).then(a.bind(null,25)).then(t=>{let{getCLS:a,getFID:n,getFCP:r,getLCP:c,getTTFB:l}=t;a(e),n(e),r(e),c(e),l(e)})};l.a.createRoot(document.getElementById("root")).render(r.a.createElement(r.a.StrictMode,null,r.a.createElement(o,null))),i()},8:function(e,t,a){e.exports=a(22)}},[[8,1,2]]]);
//# sourceMappingURL=main.44a7d5c2.chunk.js.map