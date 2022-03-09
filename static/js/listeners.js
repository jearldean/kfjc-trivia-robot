"use strict";

//  -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- DJ Most Plays -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

document.querySelector("#dj-most-plays").addEventListener("click", djMostPlays);

function djMostPlays(evt) {
  evt.preventDefault();

  const dj_id = document.querySelector("#dj-picker").value;
  const media_type = document.querySelector(".dj:checked").value;
  const url = `/dj_favorites/${media_type}/dj_id=${dj_id}`;
  const air_name = document.querySelector("#airname").value;
  console.log(air_name);
  const heading = `<h3>${air_name} plays these ${media_type}s a lot:</h3>`;

  console.log(url);

  fetch(url)
  .then(response => response.text())
  .then(status => {

    const json = JSON.parse(status);
    if (media_type == 'artist') {
      let inject_table = '<table><tr><th>Artist</th><th>Plays</th></tr>';
        for (const row of json) {
          const plays = row.plays;
          const artist = row.artist;
          const table_row = `<tr><td>${artist}</td><td>${plays}</td></tr>`;
          inject_table += table_row;
        }
      inject_table += "</table>";
      document.querySelector('#answer_window').innerHTML = `${heading}<br>${inject_table}`;
    } else if (media_type == 'album') {
      let inject_table = '<table><tr><th>Album</th><th>Plays</th></tr>';
        for (const row of json) {
          const plays = row.plays;
          const album_title = row.album_title;
          const table_row = `<tr><td>${album_title}</td><td>${plays}</td></tr>`;
          inject_table += table_row;
        }
      inject_table += "</table>";
      document.querySelector('#answer_window').innerHTML = `${heading}<br>${inject_table}`;
    } else {
      let inject_table = '<table><tr><th>Track</th><th>Plays</th></tr>';
        for (const row of json) {
          const plays = row.plays;
          const track_title = row.track_title;
          const table_row = `<tr><td>${track_title}</td><td>${plays}</td></tr>`;
          inject_table += table_row;
        }
      inject_table += "</table>";
      document.querySelector('#answer_window').innerHTML = `${heading}<br>${inject_table}`;
    }
  
  });
}

//  -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- DJ Stats -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

document.querySelector("#dj-stats-button").addEventListener("click", djStats);

function djStats(evt) {
  evt.preventDefault();

  const order_by = document.querySelector(".dj-stats:checked").value;
  /* http://0.0.0.0:5000/dj_stats/order_by=firstshow&reverse=0
     http://0.0.0.0:5000/dj_stats/order_by=lastshow&reverse=1 
     http://0.0.0.0:5000/dj_stats/order_by=showcount&reverse=1*/

  let reverse;
  if (order_by == 'firstshow') {
    reverse = '0';
  } else {
    reverse = '1';
  }

  const url = `/dj_stats/order_by=${order_by}&reverse=${reverse}`;

  console.log(url);

  fetch(url)
  .then(response => response.text())
  .then(status => {

    const json = JSON.parse(status);

    if (order_by == 'firstshow') {
      const heading = `<h3>DJs ranked by the date of their First Show:</h3>`;
      let inject_table = '<table><tr><th>Air Name</th><th>First Show</th></tr>';
        for (const row of json) {
          const air_name = row.air_name;
          const firstshow = humanReadableDate(row.firstshow);
          const table_row = `<tr><td>${air_name}</td><td>${firstshow}</td></tr>`;
          inject_table += table_row;
        }
      inject_table += "</table>";
      document.querySelector('#answer_window').innerHTML = `${heading}<br>${inject_table}`;
    } else if (order_by == 'lastshow') {
      const heading = `<h3>DJs ranked by the date of their Last Show:</h3>`;
      let inject_table = '<table><tr><th>Air Name</th><th>Last Show</th></tr>';
        for (const row of json) {
          const air_name = row.air_name;
          const lastshow = humanReadableDate(row.lastshow);
          const table_row = `<tr><td>${air_name}</td><td>${lastshow}</td></tr>`;
          inject_table += table_row;
        }
      inject_table += "</table>";
      document.querySelector('#answer_window').innerHTML = `${heading}<br>${inject_table}`;
    } else {    // order_by == 'showcount'
      const heading = `<h3>DJs ranked by Show Count:</h3>`;
      let inject_table = '<table><tr><th>Air Name</th><th>Show Count</th></tr>';
        for (const row of json) {
          const air_name = row.air_name;
          const showcount = row.showcount;
          const table_row = `<tr><td>${air_name}</td><td>${showcount}</td></tr>`;
          inject_table += table_row;
        }
      inject_table += "</table>";
      document.querySelector('#answer_window').innerHTML = `${heading}<br>${inject_table}`;
    }
  
  });
}

//  -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- Last Plays -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

document.querySelector("#artist-last-plays").addEventListener("submit", artistLastPlays);
document.querySelector("#album-last-plays").addEventListener("submit", albumLastPlays);
document.querySelector("#track-last-plays").addEventListener("submit", trackLastPlays);

function humanReadableDate(isoFormatDate) {
  const readable = new Date(
    isoFormatDate).toLocaleDateString(
      'en-us', { weekday:"long", year:"numeric", month:"short", day:"numeric"}) 
  return readable;
}

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
        const sentence = `<li>${air_name} played the track '${track_title}' from the album '${album_title}' by the artist '<span class="word_highlight">${artist}</span>' on ${human_date}.</li>`;
        sentences += sentence;
      }
  
    const heading = `<h3>Here's everything I found about Artists containing '${search_artist}':</h3>`;
    document.querySelector('#answer_window').innerHTML = `${heading}<br>${sentences}`;

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
        const sentence = `<li>${air_name} played the track '${track_title}' from the album '<span class="word_highlight">${album_title}</span>' by the artist '${artist}' on ${human_date}.</li>`;
        sentences += sentence;
      }
  
    const heading = `<h3>Here's everything I found about Albums containing '${search_album}':</h3>`;
    document.querySelector('#answer_window').innerHTML = `${heading}<br>${sentences}`;

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
        const sentence = `<li>${air_name} played the track '<span class="word_highlight">${track_title}</span>' from the album '${album_title}' by the artist '${artist}' on ${human_date}.</li>`;
        sentences += sentence;
      }

    const heading = `<h3>Here's everything I found about Tracks containing '${search_track}':</h3>`;
    document.querySelector('#answer_window').innerHTML = `${heading}<br>${sentences}`;

  });
}

//  -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- Top Plays -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

document.querySelector("#top-plays").addEventListener("submit", topPlays);

function topPlays(evt) {
  evt.preventDefault();

  const topN = document.querySelector("#top-n-int:checked").value;
  const mediaType = document.querySelector("#top-n-media-str:checked").value;
  const startDate = document.querySelector("#start-date").value;
  const endDate = document.querySelector("#end-date").value;
  const url = `/top_plays/top=${topN}&order_by=${mediaType}&start_date=${startDate}&end_date=${endDate}`;
  console.log(url);

  fetch(url)
  .then(response => response.text())
  .then(status => {

    const json = JSON.parse(status);

    let inject_table = '<table><tr><th>Plays</th><th>Artist</th><th>Album</th><th>Track</th></tr>';
      for (const row of json) {
        const plays = row.plays;
        const artist = row.artist;
        const album_title = row.album_title;
        const track_title = row.track_title;
        const table_row = `<tr><td>${plays}</td><td>${artist}</td><td>${album_title}</td><td>${track_title}</td></tr>`;
        inject_table += table_row;
      }
      inject_table += "</table>";

    const heading = `<h3>Here's the Top${topN} ${mediaType}s during that time:</h3>`;
    document.querySelector('#answer_window').innerHTML = `${heading}<br>${inject_table}`;

  });
}
