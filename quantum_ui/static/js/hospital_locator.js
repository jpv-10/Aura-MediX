navigator.geolocation.getCurrentPosition(async (position) => {

    const lat = position.coords.latitude;
    const lon = position.coords.longitude;

    const response = await fetch(`/nearby-hospitals?lat=${lat}&lon=${lon}`);

    const hospitals = await response.json();

    const container = document.getElementById("hospital-list");

    container.innerHTML = "";

    hospitals.forEach(hospital => {

        container.innerHTML += `
            <div class="hospital-card">
                <h3>${hospital.name}</h3>
                <p>${hospital.address}</p>
            </div>
        `;
    });

});