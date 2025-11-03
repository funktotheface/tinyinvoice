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

        // Update display cells
        row.querySelector('.vat-cell').textContent = vatAmount.toFixed(2);
        row.querySelector('.line-total').textContent = lineTotal.toFixed(2);

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
        <td class="vat-cell">0.00</td>
        <td class="line-total">0.00</td>
        <td><button type="button" class="text-red-500 remove-item">X</button></td>
    `;
    itemsTable.appendChild(newRow);
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
