


const addItemBtn = document.getElementById('add-item');
const itemsTable = document.getElementById('items-table').querySelector('tbody');
const totalField = document.getElementById('total');
const vatToggle = document.getElementById('vat-toggle');

function updateTotal() {
    let total = 0;
    const rows = itemsTable.querySelectorAll('tr');

    rows.forEach(row => {
    const qty = parseFloat(row.querySelector('[name="item_quantity[]"]').value) || 0;
    const price = parseFloat(row.querySelector('[name="item_price[]"]').value) || 0;
        const lineSubtotal = qty * price;

        // Calculate VAT if checkbox is ticked
        const vatRate = vatToggle.checked ? 0.2 : 0;
        const vatAmount = lineSubtotal * vatRate;
        const lineTotal = lineSubtotal + vatAmount;

        // Grab the inputs in THIS row
        const vatCell = row.querySelector('.vat-cell');       // ✅ input[name="item_vat[]"]
        const lineTotalCell = row.querySelector('.line-total'); // ✅ input[name="item_total[]"]

        // Update display cells
        vatCell.value = vatAmount.toFixed(2);
        lineTotalCell.value = lineTotal.toFixed(2); // we already added VAT above

        total += lineTotal;
    });


    totalField.value = total.toFixed(2);
}

// Add a new item row
addItemBtn.addEventListener('click', () => {
    const newRow = document.createElement('tr');
    newRow.className = 'bg-gray-100 rounded-xl shadow-inner';
    newRow.innerHTML = `
        <td class="p-2 w-2/5"><input type="text" name="item_description[]" class="w-full p-2 rounded-xl bg-gray-100 text-blue-900 shadow-inner placeholder-blue-400 border-none" required></td>
        <td class="p-2 w-1/6">
          <select name="item_type[]" class="w-full p-2 rounded-xl bg-gray-100 text-blue-900 shadow-inner border-none">
            <option value="goods" selected>Goods</option>
            <option value="service">Service</option>
          </select>
        </td>
        <td class="p-2 w-1/12"><input type="number" step="0.01" name="item_quantity[]" class="w-full p-2 rounded-xl bg-gray-100 text-blue-900 shadow-inner border-none" value="1" min="1" required></td>
        <td class="p-2 w-32"><input type="number" name="item_price[]" class="w-full p-2 rounded-xl bg-gray-100 text-blue-900 shadow-inner border-none" value="0" min="0" step="0.01" required></td>
        <td class="p-2 w-32"><input type="text" name="item_vat[]" class="w-full p-2 rounded-xl bg-gray-100 text-blue-900 shadow-inner vat-cell border-none" readonly value="0.00"></td>
        <td class="p-2 w-32"><input type="text" name="item_total[]" class="w-full p-2 rounded-xl bg-gray-100 text-blue-900 shadow-inner line-total border-none" readonly value="0.00"></td>
        <td class="p-2 w-10 text-center"><button type="button" class="text-red-500 font-bold remove-item">X</button></td>
    `;
    itemsTable.appendChild(newRow);
    // Ensure labels/placeholder reflect the selected type for the new row
    updateRowLabels(newRow);
    updateTotal(); // 👈 this line ensures the new row updates totals instantly
});


// Remove item
itemsTable.addEventListener('click', e => {
    if (e.target.classList.contains('remove-item')) {
        e.target.closest('tr').remove();
        updateTotal();
    }
});

// Update row labels/placeholders based on item type
function updateRowLabels(row) {
  const typeSelect = row.querySelector('[name="item_type[]"]');
  if (!typeSelect) return;
  const type = typeSelect.value;
  const qtyInput = row.querySelector('[name="item_quantity[]"]');
  const priceInput = row.querySelector('[name="item_price[]"]');

  if (type === 'service') {
    if (qtyInput) qtyInput.placeholder = 'Hrs';
    if (priceInput) priceInput.placeholder = '£PH';
    if (qtyInput) qtyInput.min = '0';
  } else {
    if (qtyInput) qtyInput.placeholder = 'Qty';
    if (priceInput) priceInput.placeholder = 'Price';
    if (qtyInput) qtyInput.min = '1';
  }
}

// Delegate change events to handle type switches for any row (including dynamic rows)
itemsTable.addEventListener('change', e => {
  const row = e.target.closest('tr');
  if (!row) return;
  if (e.target.matches('[name="item_type[]"]')) {
    updateRowLabels(row);
  }
  // Recompute totals on any change
  updateTotal();
});

// Update totals on input and toggle
itemsTable.addEventListener('input', updateTotal);
vatToggle.addEventListener('change', updateTotal);

particlesJS("particles-js", {
  "particles": {
    "number": {
      "value":80,
      "density": {
        "enable": true,
        "value_area": 789.15
      }
    },
    "color": {
      "value": "#00FFFF"
    },
    "shape": {
      "type": "circle",
      "stroke": {
        "width": 0,
        "color": "#000000"
      },
      "polygon": {
        "nb_sides": 5
      },
      "image": {
        "src": "img/github.svg",
        "width": 100,
        "height": 100
      }
    },
    "opacity": {
      "value": 0.49,
      "random": false,
      "anim": {
        "enable": false,
        "speed": 0.25,
        "opacity_min": 0,
        "sync": false
      }
    },
    "size": {
      "value": 2,
      "random": true,
      "anim": {
        "enable": true,
        "speed": 0.333,
        "size_min": 0,
        "sync": false
      }
    },
    "line_linked": {
      "enable": true,
      "distance": 150,
      "color": "#00FFFF",
      "opacity": 0.4,
      "width": 1
    },
    "move": {
      "enable": true,
      "speed": 0.2,
      "direction": "none",
      "random": true,
      "straight": false,
      "out_mode": "out",
      "bounce": false,
      "attract": {
        "enable": false,
        "rotateX": 600,
        "rotateY": 1200
      }
    }
  },
  "interactivity": {
    "detect_on": "canvas",
    "events": {
      "onhover": {
        "enable": true,
        "mode": "bubble"
      },
      "onclick": {
        "enable": true,
        "mode": "push"
      },
      "resize": true
    },
    "modes": {
      "grab": {
        "distance": 400,
        "line_linked": {
          "opacity": 1
        }
      },
      "bubble": {
        "distance": 83.9,
        "size": 1,
        "duration": 3,
        "opacity": 1,
        "speed": 3
      },
      "repulse": {
        "distance": 200,
        "duration": 0.4
      },
      "push": {
        "particles_nb": 4
      },
      "remove": {
        "particles_nb": 2
      }
    }
  },
  "retina_detect": true
});

// Mobile menu toggle
const mobileMenuButton = document.getElementById('mobile-menu-button');
const mobileNav = document.getElementById('mobile-nav');
if (mobileMenuButton && mobileNav) {
  mobileMenuButton.addEventListener('click', () => {
    const expanded = mobileMenuButton.getAttribute('aria-expanded') === 'true';
    mobileMenuButton.setAttribute('aria-expanded', String(!expanded));
    mobileNav.classList.toggle('hidden');
  });
  // Close mobile menu when clicking outside
  document.addEventListener('click', (e) => {
    if (!mobileNav.classList.contains('hidden')) {
      const target = e.target;
      if (!mobileNav.contains(target) && !mobileMenuButton.contains(target)) {
        mobileNav.classList.add('hidden');
        mobileMenuButton.setAttribute('aria-expanded', 'false');
      }
    }
  });
}