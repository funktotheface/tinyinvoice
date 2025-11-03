
const addItemBtn = document.getElementById('add-item');
const itemsTable = document.getElementById('items-table').querySelector('tbody');
const totalField = document.getElementById('total');

function updateTotal() {
    let total = 0;
    const quantities = document.getElementsByName('item_quantity[]');
    const prices = document.getElementsByName('item_price[]');

    for (let i = 0; i < quantities.length; i++) {
        total += parseFloat(quantities[i].value) * parseFloat(prices[i].value);
    }
    totalField.value = total.toFixed(2);
}

addItemBtn.addEventListener('click', () => {
    const newRow = document.createElement('tr');
    newRow.innerHTML = `
    <td><input type="text" name="item_description[]" class="border p-1 rounded" required></td>
    <td><input type="number" name="item_quantity[]" class="border p-1 rounded" value="1" min="1" required></td>
    <td><input type="number" name="item_price[]" class="border p-1 rounded" value="0" min="0" step="0.01" required></td>
    <td><button type="button" class="text-red-500 remove-item">X</button></td>
  `;
    itemsTable.appendChild(newRow);
});

itemsTable.addEventListener('click', (e) => {
    if (e.target.classList.contains('remove-item')) {
        e.target.closest('tr').remove();
        updateTotal();
    }
});

itemsTable.addEventListener('input', updateTotal);
