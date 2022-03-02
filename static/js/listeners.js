"use strict";


//  -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- Last Plays -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

function humanReadableDate(isoFormatDate) {
  const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
  const readable = new Date(isoFormatDate);
  const m = readable.getMonth();
  const d = readable.getDay();
  const y = readable.getFullYear();
  const mlong = months[m];
  const human_date = mlong + " " + d + ", " + y;
  return human_date;
}

document.querySelector("#artist-last-plays").addEventListener("submit", artistLastPlays);
document.querySelector("#album-last-plays").addEventListener("submit", albumLastPlays);
document.querySelector("#track-last-plays").addEventListener("submit", trackLastPlays);

function artistLastPlays(evt) {
  evt.preventDefault();

  const media_type = document.querySelector("#artist-last-plays-button").value;
  const search_artist = document.querySelector("#artist-last-plays-string").value;
  const url = `/last_played/${media_type}=${search_artist}`;
  console.log(url);

  fetch(url)
  .then(response => response.text())
  .then(status => {

    const json = JSON.parse(status);
    
    let sentences = "";
      for (const row of json) {
        const air_name = row.air_name;
        const track_title = row.track_title;
        const album_title = row.album_title;
        const artist = row.artist;
        const human_date = humanReadableDate(row.time_played);
        const sentence = `<li>${air_name} played the track '${track_title}' from the album '${album_title}' by the artist '${artist}' on ${human_date}.</li>`;
        sentences += sentence;
      }
  
    document.querySelector('#requested_stat').innerHTML = sentences;

  });
}


function albumLastPlays(evt) {
  evt.preventDefault();

  const media_type = document.querySelector("#album-last-plays-button").value;
  const search_album = document.querySelector("#album-last-plays-string").value;
  const url = `/last_played/${media_type}=${search_album}`;
  console.log(url);

  fetch(url)
  .then(response => response.text())
  .then(status => {

    const json = JSON.parse(status);
    
    let sentences = "";
      for (const row of json) {
        const air_name = row.air_name;
        const track_title = row.track_title;
        const album_title = row.album_title;
        const artist = row.artist;
        const human_date = humanReadableDate(row.time_played);
        const sentence = `<li>${air_name} played the track '${track_title}' from the album '${album_title}' by the artist '${artist}' on ${human_date}.</li>`;
        sentences += sentence;
      }
  
    document.querySelector('#requested_stat').innerHTML = sentences;

  });
}



function trackLastPlays(evt) {
  evt.preventDefault();

  const media_type = document.querySelector("#track-last-plays-button").value;
  const search_track = document.querySelector("#track-last-plays-string").value;
  const url = `/last_played/${media_type}=${search_track}`;
  console.log(url);

  fetch(url)
  .then(response => response.text())
  .then(status => {

    const json = JSON.parse(status);
    
    let sentences = "";
      for (const row of json) {
        const air_name = row.air_name;
        const track_title = row.track_title;
        const album_title = row.album_title;
        const artist = row.artist;
        const human_date = humanReadableDate(row.time_played);
        const sentence = `<li>${air_name} played the track '${track_title}' from the album '${album_title}' by the artist '${artist}' on ${human_date}.</li>`;
        sentences += sentence;
      }
  
    document.querySelector('#requested_stat').innerHTML = sentences;

  });
}


//  -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- Top Plays -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

document.querySelector("#top-plays").addEventListener("click", topPlays);

function topPlays(evt) {
  evt.preventDefault();

  const topN = document.querySelector("#top-n-int").value;
  const mediaType = document.querySelector("#top-n-media-str").value;
  const startDate = document.querySelector("#start-date").value;
  const endDate = document.querySelector("#end-date").value;
  const url = `/top_plays/top=${topN}&order_by=${mediaType}&start_date=${startDate}&end_date=${endDate}`;
  console.log(url);

  fetch(url)
  .then(response => response.text())
  .then(status => {
    console.log(status);
    const json = JSON.parse(status);
    
    let sentences = '<table><tr><th>Plays</th><th>Artist</th><th>Album</th><th>Track</th></tr>';
      for (const row of json) {
        const plays = row.plays;
        const artist = row.artist;
        const album_title = row.album_title;
        const track_title = row.track_title;
        const sentence = `<tr><td>${plays}</td><td>${artist}</td><td>${album_title}</td><td>${track_title}</td></tr>`;
        sentences += sentence;
      }
    sentences += "</table>";
  
    document.querySelector('#requested_stat').innerHTML = sentences;

  });
}
