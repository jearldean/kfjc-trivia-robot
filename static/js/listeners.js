"use strict";


function djInfo(evt) {
  evt.preventDefault();

  const order_by = document.querySelector("#pick-dj-stat").value;
  console.log(order_by);
  const url = `/dj_stats/order_by=${order_by}&reverse=1`;
  console.log(url);

  //"air_name", "dj_id", "showcount", "firstshow", "lastshow"

  fetch(url)
  .then(response => response.text())
  .then(status => {

     const display_answer = [];

    for (const row of status) {
      
      const row_items = [];
      
      for (const row_item of row) {
        row_items.push(row_item["air_name"]);
        row_items.push(row_item["show_count"]);
      }

      display_answer.push(row_items);
    } 

    document.querySelector('#dj-text').innerHTML = display_answer;

  });
}

document.querySelector("#dj-submit").addEventListener("click", djInfo);
