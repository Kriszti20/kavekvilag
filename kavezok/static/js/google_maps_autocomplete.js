function initAutocomplete() {
    const input = document.getElementById("id_cim"); // Django automatikusan "id_" prefixet ad a mező nevéhez
    const autocomplete = new google.maps.places.Autocomplete(input);

    // Autocomplete esemény figyelése
    autocomplete.addListener("place_changed", function () {
        const place = autocomplete.getPlace();
        console.log("Kiválasztott cím:", place.formatted_address);
    });
}