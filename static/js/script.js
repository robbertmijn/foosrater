document.getElementById('date_time').value = new Date().toISOString().slice(0, 19);
document.getElementById('foosform').addEventListener('submit', function(event) {
    const dropdown1 = parseInt(document.getElementById('blue_score').value);
    const dropdown2 = parseInt(document.getElementById('red_score').value);
    const sum = dropdown1 + dropdown2;

    if (sum < 1) {
        event.preventDefault();
        document.getElementById('error-message').style.display = 'block';
    } else {
        document.getElementById('error-message').style.display = 'none';
    }
})

document.addEventListener("DOMContentLoaded", function() {
    // Get the hidden div
    let configDiv = document.getElementById("config");

    // Extract Jinja variables from data attributes
    let leagueName = configDiv.getAttribute("data-league-name");

});


function fetchData(name) {
    fetch(`/${leagueName}/player/${name}`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('overlay3Label').textContent = data.name;
            
            const listContainer1 = document.getElementById('list-opponents');
            listContainer1.innerHTML = '';
            data.opponents.forEach(item => {
                const listItem = document.createElement('li');
                listItem.textContent = `${item[0]}: ${item[1].opponent} (kill-death ratio: ${(item[1].made/item[1].let).toFixed(2)})`;
                listContainer1.appendChild(listItem);
            });

            const listContainer2 = document.getElementById('list-teammates');
            listContainer2.innerHTML = '';
            data.teammates.forEach(item => {
                const listItem = document.createElement('li');
                listItem.textContent = `${item[0]}: ${item[1]}`;
                listContainer2.appendChild(listItem);
            });

        })
        .catch(error => {
            console.error('Error fetching data:', error);
        });
}

document.querySelectorAll('.name-link').forEach(item => {
    item.addEventListener('click', function() {
        const name = this.getAttribute('data-name');
        console.log(name)
        fetchData(name);  // Call fetch function with the clicked word
    });
});

function sendPostRequest(url) {
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
    }).then(response => {
        if (response.ok) {
            location.reload(); // Reload the page or handle success
        } else {
            alert('Failed to delete the game.');
        }
    }).catch(error => {
        console.error('Error:', error);
    });
}   

function toggleMenu() {
    let menu = document.getElementById("menu");
    if (menu.style.display === "none" || menu.style.display === "") {
        menu.style.display = "flex";
    } else {
        menu.style.display = "none";
    }
}
