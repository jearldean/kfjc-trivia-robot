function djMostPlays(evt) {
  evt.preventDefault();

  const data = {
    dj: document.querySelector('#dj-field').value,
  };

  fetch('/ajax', {
    method: 'GET',
    body: JSON.stringify(data),
    headers: {
      'Content-Type': 'application/json',
    },
  })
  .then(response => response.json())
  .then(response => {
    document.querySelector("#dj-most-plays").innerHTML = 
    `<p>
    dj: ${response.dj}<br>
    </p>`;
  }
  );
}

document.querySelector('#dj-info').addEventListener('submit', djMostPlays);
document.querySelector('#dj-most-plays').addEventListener('submit', djMostPlays);
document.querySelector('#artist-last-plays').addEventListener('submit', artistLastPlays);
document.querySelector('#album-last-plays').addEventListener('submit', albumLastPlays);
document.querySelector('#track-last-plays').addEventListener('submit', trackLastPlays);
document.querySelector('#top-plays').addEventListener('submit', topPlays);
