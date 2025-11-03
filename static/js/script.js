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
    newRow.innerHTML = `
        <td><input type="text" name="item_description[]" class="border p-1 rounded" required></td>
        <td><input type="number" name="item_quantity[]" class="border p-1 rounded" value="1" min="1" required></td>
        <td><input type="number" name="item_price[]" class="border p-1 rounded" value="0" min="0" step="0.01" required></td>
        <td><input type="text" name="item_vat[]" class="border p-1 rounded vat-cell" readonly value="0.00"></td>
        <td><input type="text" name="item_total[]" class="border p-1 rounded line-total" readonly value="0.00"></td>
        <td><button type="button" class="text-red-500 remove-item">X</button></td>
    `;
    itemsTable.appendChild(newRow);
    updateTotal(); // 👈 this line ensures the new row updates totals instantly
});


// Remove item
itemsTable.addEventListener('click', e => {
    if (e.target.classList.contains('remove-item')) {
        e.target.closest('tr').remove();
        updateTotal();
    }
});

// Update totals on input and toggle
itemsTable.addEventListener('input', updateTotal);
vatToggle.addEventListener('change', updateTotal);
