function filterByPrice(price) {
    price = parseFloat(price);

    let range;
    if (price <= 10000) {
        range = 'up_to_10000';
    } else if (price <= 40000) {
        range = 'from10000_to40000';
    } else if (price <= 100000) {
        range = 'from40000_to100000';
    } else {
        range = 'over_100000';
    }

    window.location.href = `?price_range=${range}`;
}

function filterByMeters(meters) {
    meters = parseFloat(meters);

    let range;
    if (meters <= 25) {
        range = 'up_to25met';
    } else if (meters <= 40) {
        range = 'from25met_to40met';
    } else if (meters <= 75) {
        range = 'from40met_to75met';
    } else {
        range = 'over_75met';
    }

    window.location.href = `?meters_range=${range}`;
}

document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('.search-form');
    if (!form) return;

    form.addEventListener('submit', function (event) {
        const priceInput = form.querySelector('input[name="price"]');
        const priceValue = parseFloat(priceInput.value);

        if (!priceInput.value || isNaN(priceValue)) {
            return;
        }

        let range = '';
        if (priceValue <= 10000) {
            range = 'up_to_10000';
        } else if (priceValue <= 40000) {
            range = 'from10000_to40000';
        } else if (priceValue <= 100000) {
            range = 'from40000_to100000';
        } else {
            range = 'over_100000';
        }

        priceInput.remove();

        const hiddenInput = document.createElement('input');
        hiddenInput.type = 'hidden';
        hiddenInput.name = 'price_range';
        hiddenInput.value = range;
        form.appendChild(hiddenInput);
    });
});