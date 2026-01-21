// Real-time update of remaining stock when approved quantity changes
(function() {
    'use strict';
    
    function updateRemainingStock() {
        const approvedQtyInput = document.getElementById('id_approved_quantity');
        const requestedQtyInput = document.getElementById('id_quantity_required');
        
        if (!approvedQtyInput) return;
        
        // Get current stock value from the readonly field
        const currentStockField = document.querySelector('.field-current_stock .readonly');
        if (!currentStockField) return;
        
        const currentStockText = currentStockField.textContent.trim();
        const currentStock = parseInt(currentStockText.replace(/[^\d]/g, '')) || 0;
        
        // Get requested quantity
        const requestedQty = parseInt(requestedQtyInput.value) || 0;
        
        // Function to calculate and update display
        function updateDisplay() {
            const approvedQty = parseInt(approvedQtyInput.value) || null;
            const qtyToSend = approvedQty !== null ? approvedQty : requestedQty;
            const remaining = currentStock - qtyToSend;
            
            // Update the remaining_after_approved field
            const remainingField = document.querySelector('.field-remaining_after_approved .readonly');
            if (remainingField) {
                const color = remaining >= 0 ? 'green' : 'red';
                remainingField.innerHTML = `<span style="color: ${color}; font-weight: bold;">${remaining} PCS</span>`;
            }
        }
        
        // Add event listener for real-time updates
        approvedQtyInput.addEventListener('input', updateDisplay);
        approvedQtyInput.addEventListener('change', updateDisplay);
        
        // Initial update
        updateDisplay();
    }
    
    // Run when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', updateRemainingStock);
    } else {
        updateRemainingStock();
    }
})();
