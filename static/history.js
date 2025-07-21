document.addEventListener('DOMContentLoaded', function() {
    const historyList = document.getElementById('history-list');
    
    try {
        const history = JSON.parse(localStorage.getItem('history') || '[]');

        if (history.length === 0) {
            historyList.innerHTML = '<p>Henüz işlem yapılmadı.</p>';
            return;
        }

        // Geçmiş işlemleri temizleme fonksiyonu
        function clearHistory() {
            if (confirm('Tüm geçmiş işlemleri silmek istediğinizden emin misiniz?')) {
                localStorage.removeItem('history');
                historyList.innerHTML = '<p>Henüz işlem yapılmadı.</p>';
            }
        }

        // Tek bir işlemi silme fonksiyonu
        function deleteItem(index) {
            if (confirm('Bu işlemi silmek istediğinizden emin misiniz?')) {
                const itemElement = document.querySelector(`[data-index="${index}"]`);
                if (itemElement) {
                    // Silme animasyonu
                    itemElement.classList.add('deleting');
                    
                    setTimeout(() => {
                        const updatedHistory = history.filter((_, i) => i !== index);
                        localStorage.setItem('history', JSON.stringify(updatedHistory));
                        
                        // Sayfayı yenilemek yerine DOM'u güncelle
                        if (updatedHistory.length === 0) {
                            historyList.innerHTML = '<p>Henüz işlem yapılmadı.</p>';
                        } else {
                            // Sadece silinen elementi kaldır
                            itemElement.remove();
                            
                            // Kalan elementlerin data-index'lerini güncelle
                            const remainingItems = document.querySelectorAll('.history-item');
                            remainingItems.forEach((item, newIndex) => {
                                const oldIndex = parseInt(item.getAttribute('data-index'));
                                if (oldIndex > index) {
                                    item.setAttribute('data-index', oldIndex - 1);
                                    // Delete butonunun onclick'ini güncelle
                                    const deleteBtn = item.querySelector('.delete-btn');
                                    if (deleteBtn) {
                                        deleteBtn.onclick = () => deleteItem(oldIndex - 1);
                                    }
                                }
                            });
                        }
                    }, 500); // Animasyon süresi
                }
            }
        }

        // Temizleme butonu ekle
        const clearButton = document.createElement('div');
        clearButton.innerHTML = `
            <button onclick="clearHistory()" style="background: linear-gradient(90deg, #ff4757, #ff3742); margin-bottom: 20px;">
                🗑️ Tüm Geçmişi Temizle (${history.length} işlem)
            </button>
        `;
        historyList.appendChild(clearButton);

        // Geçmiş işlemleri listele
        history.forEach((item, index) => {
            const box = document.createElement('div');
            box.classList.add('image-box', 'fade-in', 'history-item');
            box.style.animationDelay = `${index * 0.1}s`;
            box.setAttribute('data-index', index);
            
            // Güvenli görüntü yükleme
            const imgElement = document.createElement('img');
            imgElement.src = item.annotated_image;
            imgElement.alt = 'Geçmiş Görsel';
            imgElement.onerror = function() {
                this.style.display = 'none';
                this.nextElementSibling.textContent = 'Görsel yüklenemedi';
            };
            
            box.innerHTML = `
                <div class="history-header">
                    <h3>${item.timestamp || 'Bilinmeyen Tarih'}</h3>
                    <button class="delete-btn" onclick="deleteItem(${index})" title="Bu işlemi sil">
                        ❌
                    </button>
                </div>
            `;
            box.appendChild(imgElement);
            box.innerHTML += `
                <p><strong>OCR:</strong> ${item.plate_text || 'Okunamadı'}</p>
                <p><strong>Güven:</strong> ${item.confidence || 0}%</p>
            `;
            
            historyList.appendChild(box);
        });

        // Global fonksiyonları window objesine ekle
        window.clearHistory = clearHistory;
        window.deleteItem = deleteItem;

    } catch (error) {
        console.error('History yüklenirken hata:', error);
        historyList.innerHTML = '<p>Geçmiş yüklenirken bir hata oluştu.</p>';
    }
});