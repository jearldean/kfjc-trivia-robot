"use strict";

function djFavorite(evt) {
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
      /* 
      const row_items = [];
      
      for (const row_item of row) {
        row_items.push(row_item["air_name"]);
        row_items.push(row_item["show_count"]);
      }
 */
      display_answer.push(row);
    } 

    document.querySelector('#requested_stat').innerHTML = display_answer;

  });
}

document.querySelector("#dj-most-plays").addEventListener("click", djFavorite);
document.querySelector("#artist-last-plays").addEventListener("click", lastPlays);
document.querySelector("#album-last-plays").addEventListener("click", lastPlays);
document.querySelector("#track-last-plays").addEventListener("click", lastPlays);
document.querySelector("#top-plays").addEventListener("click", topPlays);



function lastPlays(evt) {
  evt.preventDefault();

  const top = document.querySelector("#top-n").value;
  const topPlays = document.querySelector("#top-plays").value;
  const startDate = document.querySelector("#start_date").value;
  const endDate = document.querySelector("#end_date").value;

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
      /* 
      const row_items = [];
      
      for (const row_item of row) {
        row_items.push(row_item["air_name"]);
        row_items.push(row_item["show_count"]);
      }
 */
      display_answer.push(row);
    } 

    document.querySelector('#requested_stat').innerHTML = display_answer;

  });
}




function topPlays(evt) {
  evt.preventDefault();

  const top = document.querySelector("#top-n").value;
  const topPlays = document.querySelector("#top-plays").value;
  const startDate = document.querySelector("#start_date").value;
  const endDate = document.querySelector("#end_date").value;

  const url = `/top_${topPlays}s/top=${top}&start_date=${startDate}&end_date=${endDate}`;
  console.log(url);

  fetch(url)
  .then(response => response.text())
  .then(status => {

     const display_answer = [];

    for (const row of status) {
      /* 
      const row_items = [];
      
      for (const row_item of row) {
        row_items.push(row_item["air_name"]);
        row_items.push(row_item["show_count"]);
      }
 */
      display_answer.push(row);
    } 

    document.querySelector('#requested_stat').innerHTML = display_answer;

  });
}
