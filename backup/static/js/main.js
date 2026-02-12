/**
 * Premium Showcase - 통합 JavaScript
 * 이 파일이 모든 페이지의 기능을 담당합니다.
 * loader.js가 이 파일을 로드합니다.
 * XSS 방지: 모든 사용자 입력은 escapeHtml()로 이스케이프 후 삽입
 */

(function () {
  'use strict';

  // === XSS 방지: HTML 이스케이프 ===
  function escapeHtml(str) {
    if (str == null) return '';
    var s = String(str);
    return s
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  // 이미지 URL 검증 (javascript:, data:text/html 등 차단)
  function isValidImageUrl(url) {
    if (!url || typeof url !== 'string') return false;
    var u = url.trim().toLowerCase();
    if (u.startsWith('https://') || u.startsWith('http://')) return true;
    if (u.startsWith('data:image/')) return true;
    return false;
  }

  function safeImageUrl(url) {
    return isValidImageUrl(url) ? url : '';
  }
  function safeLinkUrl(url) {
    if (!url || typeof url !== 'string') return '';
    var u = url.trim().toLowerCase();
    if (u.startsWith('https://') || u.startsWith('http://')) return url.trim();
    return '';
  }
  // 가격: 저장값(문자열/숫자) → 숫자 (0 = 무료)
  function parsePriceNum(price) {
    if (price == null) return 0;
    var s = String(price).trim();
    if (!s) return 0;
    if (/^무료/i.test(s)) return 0;
    var n = parseInt(s.replace(/[^\d]/g, ''), 10);
    return isNaN(n) ? 0 : n;
  }

  // 숫자 → 천단위 콤마
  function formatPriceComma(n) {
    return Math.floor(Number(n) || 0).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
  }

  // 표시용: 0원 → "0원 [ 무료 ]", 1원 이상 → "1,000원 [ 유료 ]"
  function formatPriceDisplay(price) {
    var n = parsePriceNum(price);
    if (n === 0) return { text: '0원 [ 무료 ]', paid: false };
    return { text: formatPriceComma(n) + '원 [ 유료 ]', paid: true };
  }

  function priceTagHtml(price) {
    var res = formatPriceDisplay(price);
    if (!res.text) return '';
    var cls = res.paid ? 'product-price product-price--paid' : 'product-price product-price--free';
    return '<p class="' + cls + '">' + escapeHtml(res.text) + '</p>';
  }

  // === Toast 알림 ===
  function toast(message, type) {
    type = type || 'success';
    var el = document.createElement('div');
    el.className = 'toast ' + type;
    el.textContent = message;
    document.body.appendChild(el);
    setTimeout(function () {
      el.style.opacity = '0';
      setTimeout(function () { el.remove(); }, 300);
    }, 3000);
  }

  // === API 호출 헬퍼 ===
  function api(url, options) {
    options = options || {};
    var opts = {
      headers: { 'Content-Type': 'application/json' },
      method: options.method || 'GET',
    };
    var session = localStorage.getItem('adminSession');
    if (session) opts.headers['Authorization'] = 'Bearer ' + session;
    if (options.body) opts.body = JSON.stringify(options.body);
    return fetch(url, opts).then(function (r) {
      return r.json().then(function (data) {
        if (r.status === 401 && session) {
          localStorage.removeItem('adminSession');
          var msg = '로그인이 만료되었습니다. 다시 로그인해 주세요.';
          if (window.location.pathname.indexOf('/admin') === 0) {
            toast(msg, 'error');
            setTimeout(function () { window.location.href = '/admin'; }, 800);
          }
          throw new Error(msg);
        }
        if (!r.ok) throw new Error(data.error || 'Request failed');
        return data;
      });
    });
  }

  function renderProductCard(p, i) {
    var imgUrl = safeImageUrl(p.image);
    return (
      '<div class="product-card group relative" data-product="' + encodeURIComponent(JSON.stringify(p)) + '" data-index="' + i + '">' +
      '<div class="glass-effect holographic-border rounded-2xl overflow-hidden">' +
      '  <div class="product-card-image relative overflow-hidden bg-card/50">' +
      '    <img src="' + escapeHtml(imgUrl) + '" alt="' + escapeHtml(p.name || '') + '" class="w-full h-full object-cover product-img">' +
      '    <div class="absolute inset-0 bg-gradient-to-t from-card via-transparent to-transparent opacity-60"></div>' +
      '    <div class="absolute top-4 right-4 text-9xl font-display font-bold text-primary/10 leading-none">' + escapeHtml(String(p.id || '').padStart(2, '0')) + '</div>' +
      '  </div>' +
      '  <div class="product-card-body">' +
      '    <p class="accent-text text-xs text-muted-foreground mb-2 tracking-wider uppercase">' + escapeHtml(p.code || '') + '</p>' +
      '    <h3 class="text-3xl font-display font-bold mb-1">' + escapeHtml(p.name || '') + '</h3>' +
      '    <p class="text-primary accent-text text-sm">' + escapeHtml(p.category || '') + '</p>' +
      '    <p class="text-muted-foreground mb-6 leading-relaxed">' + escapeHtml((p.description || '').substring(0, 100)) + '</p>' +
      '    <div class="flex flex-wrap gap-2 mb-4">' +
      (p.specs || []).map(function (s) { return '<span class="badge">' + escapeHtml(s) + '</span>'; }).join('') +
      '    </div>' +
      '    <div class="product-card-price-wrap">' + (p ? priceTagHtml(p.price) : '') + '</div>' +
      '    <button type="button" class="btn btn-outline w-full product-detail-btn">자세히 보기</button>' +
      '  </div>' +
      '</div></div>'
    );
  }

  function renderProductsGrid(productsEl, products) {
    if (!products || products.length === 0) {
      productsEl.innerHTML = '<div class="text-center py-12 text-muted-foreground">검색 결과가 없습니다.</div>';
      return;
    }
    productsEl.innerHTML = products.map(function (p, i) { return renderProductCard(p, i); }).join('');
    attachProductCardListeners();
  }

  // === Home 페이지 ===
  function initHome() {
    var productsEl = document.getElementById('products-grid');
    var searchInput = document.getElementById('product-search-input');
    var searchBtn = document.getElementById('product-search-btn');
    if (!productsEl) return;

    var mousePosition = { x: 0, y: 0 };
    window.addEventListener('mousemove', function (e) {
      mousePosition.x = (e.clientX / window.innerWidth - 0.5) * 2;
      mousePosition.y = (e.clientY / window.innerHeight - 0.5) * 2;
    });

    var allProducts = [];
    api('/api/products')
      .then(function (products) {
        allProducts = products || [];
        if (allProducts.length === 0) {
          productsEl.innerHTML = '<div class="text-center py-12 text-muted-foreground">제품이 없습니다.</div>';
          return;
        }
        renderProductsGrid(productsEl, allProducts);

        function doSearch() {
          var q = (searchInput && searchInput.value) ? searchInput.value.trim().toLowerCase() : '';
          if (!q) {
            renderProductsGrid(productsEl, allProducts);
            return;
          }
          var filtered = allProducts.filter(function (p) {
            return (p.name || '').toLowerCase().indexOf(q) !== -1 ||
              (p.code || '').toLowerCase().indexOf(q) !== -1 ||
              (p.category || '').toLowerCase().indexOf(q) !== -1;
          });
          renderProductsGrid(productsEl, filtered);
        }
        if (searchBtn) searchBtn.addEventListener('click', doSearch);
        if (searchInput) {
          searchInput.addEventListener('input', doSearch);
          searchInput.addEventListener('keypress', function (e) { if (e.key === 'Enter') doSearch(); });
        }
      })
      .catch(function () {
        productsEl.innerHTML = '<div class="text-center py-12 text-muted-foreground">로딩 중 오류가 발생했습니다.</div>';
      });
  }

  function attachProductCardListeners() {
    document.querySelectorAll('.product-detail-btn').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var card = btn.closest('.product-card');
        var enc = card.getAttribute('data-product');
        var product = {};
        try {
          if (enc) product = JSON.parse(decodeURIComponent(enc));
        } catch (e) { /* invalid data - ignore */ }
        openProductDialog(product);
      });
    });
  }

  function openProductDialog(product) {
    var existing = document.getElementById('product-dialog');
    if (existing) existing.remove();
    var imgUrl = safeImageUrl(product && product.image);
    var desc = escapeHtml((product && (product.detailedDescription || product.description)) || '');
    var featuresHtml = (product && product.features && product.features.length)
      ? '<div class="product-dialog-section"><h4 class="product-dialog-section-title">주요 특징</h4><ul class="product-dialog-features">' +
        product.features.map(function (f) { return '<li>' + escapeHtml(f) + '</li>'; }).join('') + '</ul></div>'
      : '';
    var specsHtml = '<div class="product-dialog-section"><h4 class="product-dialog-section-title">제품 사양</h4><div class="product-dialog-specs">' +
      ((product && product.specs) || []).map(function (s) { return '<span class="badge">' + escapeHtml(s) + '</span>'; }).join('') + '</div></div>';
    var downloadUrl = product && product.downloadUrl ? safeLinkUrl(product.downloadUrl) : '';
    var downloadBtnHtml = downloadUrl
      ? '<a href="' + escapeHtml(downloadUrl) + '" target="_blank" rel="noopener noreferrer" class="btn btn-primary">다운로드</a>'
      : '';
    var html =
      '<div id="product-dialog" class="dialog-overlay product-dialog open">' +
      '  <div class="dialog-content glass-effect">' +
      '    <button type="button" class="product-dialog-close-x" data-dialog-close aria-label="닫기">×</button>' +
      '    <div class="product-dialog-header">' +
      '      <div class="product-dialog-image-wrap">' +
      '        <img src="' + escapeHtml(imgUrl) + '" alt="">' +
      '      </div>' +
      '      <div class="product-dialog-meta">' +
      '        <p class="product-dialog-code">' + escapeHtml((product && product.code) || '') + '</p>' +
      '        <h3 class="product-dialog-title">' + escapeHtml((product && product.name) || '') + '</h3>' +
      '        <p class="product-dialog-category">' + escapeHtml((product && product.category) || '') + '</p>' +
      (product ? priceTagHtml(product.price) : '') +
      '      </div>' +
      '    </div>' +
      '    <div class="product-dialog-body">' +
      '      <div class="product-dialog-section"><h4 class="product-dialog-section-title">상품 설명</h4><p class="product-dialog-desc">' + desc + '</p></div>' +
      featuresHtml + specsHtml +
      '    </div>' +
      '    <div class="product-dialog-actions">' +
      downloadBtnHtml +
      '      <button type="button" class="btn btn-outline" data-dialog-close>닫기</button>' +
      '    </div>' +
      '  </div></div>';
    document.body.insertAdjacentHTML('beforeend', html);
    document.getElementById('product-dialog').addEventListener('click', function (e) {
      var d = document.getElementById('product-dialog');
      if (!d) return;
      var isBackdrop = e.target === d;
      var isCloseControl = e.target.closest('[data-dialog-close]');
      if (isBackdrop || isCloseControl) {
        d.classList.remove('open');
        setTimeout(function () { d.remove(); }, 200);
      }
    });
  }

  // === Admin Login ===
  function initAdminLogin() {
    var form = document.getElementById('admin-login-form');
    if (!form) return;
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var username = (form.querySelector('[name="username"]') || {}).value || '';
      var password = (form.querySelector('[name="password"]') || {}).value || '';
      var errEl = form.querySelector('.login-error');
      var btn = form.querySelector('button[type="submit"]');
      if (errEl) { errEl.textContent = ''; errEl.style.display = 'none'; }
      btn.disabled = true;
      btn.textContent = '로그인 중...';
      api('/api/admin/login', { method: 'POST', body: { username: username, password: password } })
        .then(function (data) {
          localStorage.setItem('adminSession', data.sessionId);
          window.location.href = '/admin/dashboard';
        })
        .catch(function () {
          if (errEl) {
            errEl.textContent = '아이디 또는 비밀번호가 올바르지 않습니다.';
            errEl.style.display = 'block';
          }
          btn.disabled = false;
          btn.textContent = '로그인';
        });
    });
  }

  // === Admin Dashboard ===
  function initAdminDashboard() {
    if (!localStorage.getItem('adminSession')) {
      window.location.href = '/admin';
      return;
    }

    var productsEl = document.getElementById('admin-products-tbody');
    var addBtn = document.getElementById('admin-add-btn');
    var logoutBtn = document.getElementById('admin-logout-btn');
    var dialog = document.getElementById('admin-product-dialog');
    var dialogForm = document.getElementById('admin-product-form');

    if (dialog && dialog.parentNode !== document.body) {
      document.body.appendChild(dialog);
    }

    function loadProducts() {
      api('/api/products').then(function (products) {
        if (!productsEl) return;
        if (products.length === 0) {
          productsEl.innerHTML = '<tr><td colspan="5" class="text-center py-8 text-muted-foreground">제품이 없습니다. 제품을 추가해주세요.</td></tr>';
          return;
        }
        productsEl.innerHTML = products.map(function (p) {
          return '<tr><td>' + escapeHtml(String(p.id)) + '</td><td class="font-medium">' + escapeHtml(p.name || '') + '</td><td>' + escapeHtml(p.category || '') + '</td><td>' + escapeHtml(p.code || '') + '</td><td><div class="flex gap-2 flex-wrap">' +
            '<button type="button" class="btn btn-outline btn-sm admin-edit-btn" data-id="' + escapeHtml(String(p.id)) + '" data-product="' + encodeURIComponent(JSON.stringify(p)) + '">수정</button>' +
            '<button type="button" class="btn btn-ghost btn-sm admin-delete-btn text-destructive" data-id="' + escapeHtml(String(p.id)) + '">삭제</button></div></td></tr>';
        }).join('');
        document.querySelectorAll('.admin-edit-btn').forEach(function (b) {
          b.addEventListener('click', function () {
            var enc = b.getAttribute('data-product');
            var p = null;
            try {
              if (enc) p = JSON.parse(decodeURIComponent(enc));
            } catch (e) { /* invalid data */ }
            openEditDialog(p);
          });
        });
        document.querySelectorAll('.admin-delete-btn').forEach(function (b) {
          b.addEventListener('click', function () { handleDelete(Number(b.getAttribute('data-id'))); });
        });
      }).catch(function () { toast('제품을 불러오는데 실패했습니다.', 'error'); });
    }

    function openEditDialog(product) {
      if (!dialogForm) return;
      dialogForm.dataset.editingId = product ? String(product.id) : '';
      var titleEl = document.getElementById('dialog-title');
      var submitBtn = dialogForm.querySelector('button[type="submit"]');
      if (titleEl) titleEl.textContent = product ? '제품 수정' : '제품 추가';
      if (submitBtn) submitBtn.textContent = product ? '수정' : '추가';
      ['name', 'category', 'description', 'detailedDescription', 'code', 'downloadUrl'].forEach(function (k) {
        var el = dialogForm.querySelector('[name="' + k + '"]');
        if (el) el.value = product ? (product[k] || '') : '';
      });
      var priceEl = dialogForm.querySelector('[name="price"]');
      if (priceEl) priceEl.value = product ? String(parsePriceNum(product.price)) : '';
      var specsContainer = dialogForm.querySelector('.specs-list');
      var featuresContainer = dialogForm.querySelector('.features-list');
      if (specsContainer) specsContainer.innerHTML = ((product && product.specs) || []).map(function (s) {
        return '<span class="badge flex items-center gap-2"><span>' + escapeHtml(String(s)) + '</span><button type="button" class="remove-spec">×</button></span>';
      }).join('');
      if (featuresContainer) featuresContainer.innerHTML = ((product && product.features) || []).map(function (f) {
        return '<span class="badge flex items-center gap-2"><span>' + escapeHtml(String(f)) + '</span><button type="button" class="remove-feature">×</button></span>';
      }).join('');
      var imgPreview = dialogForm.querySelector('.img-preview');
      if (imgPreview) {
        var prevImg = safeImageUrl(product && product.image);
        imgPreview.style.display = prevImg ? 'block' : 'none';
        imgPreview.src = prevImg;
      }
      if (dialog) {
        window.scrollTo(0, 0);
        dialog.scrollTop = 0;
        dialog.setAttribute('aria-hidden', 'false');
        dialog.classList.add('open');
      }
      attachSpecFeatureListeners();
    }

    function attachSpecFeatureListeners() {
      if (!dialogForm) return;
      var specInput = dialogForm.querySelector('.spec-input');
      var featureInput = dialogForm.querySelector('.feature-input');
      var addSpec = dialogForm.querySelector('.add-spec-btn');
      var addFeature = dialogForm.querySelector('.add-feature-btn');
      var specsList = dialogForm.querySelector('.specs-list');
      var featuresList = dialogForm.querySelector('.features-list');

      function getSpecs() {
        return Array.from(specsList.querySelectorAll('.badge')).map(function (b) { return b.querySelector('span') && b.querySelector('span').textContent; }).filter(Boolean);
      }
      function getFeatures() {
        return Array.from(featuresList.querySelectorAll('.badge')).map(function (b) { return b.querySelector('span') && b.querySelector('span').textContent; }).filter(Boolean);
      }
      function addSpecTag() {
        var v = specInput && specInput.value.trim();
        if (v) {
          specsList.insertAdjacentHTML('beforeend', '<span class="badge flex items-center gap-2"><span>' + escapeHtml(v) + '</span><button type="button" class="remove-spec">×</button></span>');
          specInput.value = '';
          specsList.querySelectorAll('.remove-spec').forEach(function (b) {
            b.onclick = function () { b.closest('.badge').remove(); };
          });
        }
      }
      function addFeatureTag() {
        var v = featureInput && featureInput.value.trim();
        if (v) {
          featuresList.insertAdjacentHTML('beforeend', '<span class="badge flex items-center gap-2"><span>' + escapeHtml(v) + '</span><button type="button" class="remove-feature">×</button></span>');
          featureInput.value = '';
          featuresList.querySelectorAll('.remove-feature').forEach(function (b) {
            b.onclick = function () { b.closest('.badge').remove(); };
          });
        }
      }
      if (addSpec) addSpec.onclick = addSpecTag;
      if (addFeature) addFeature.onclick = addFeatureTag;
      if (specInput) specInput.onkeypress = function (e) { if (e.key === 'Enter') { e.preventDefault(); addSpecTag(); } };
      if (featureInput) featureInput.onkeypress = function (e) { if (e.key === 'Enter') { e.preventDefault(); addFeatureTag(); } };
      specsList.querySelectorAll('.remove-spec').forEach(function (b) { b.onclick = function () { b.closest('.badge').remove(); }; });
      featuresList.querySelectorAll('.remove-feature').forEach(function (b) { b.onclick = function () { b.closest('.badge').remove(); }; });
    }

    function handleDelete(id) {
      if (!confirm('정말 삭제하시겠습니까?')) return;
      api('/api/products/' + id, { method: 'DELETE' })
        .then(function () { toast('제품이 삭제되었습니다.'); loadProducts(); })
        .catch(function () { toast('삭제에 실패했습니다.', 'error'); });
    }

    var priceInput = dialogForm && dialogForm.querySelector('[name="price"]');
    if (priceInput) {
      priceInput.addEventListener('input', function () {
        this.value = this.value.replace(/[^0-9]/g, '');
      });
    }
    if (addBtn) addBtn.addEventListener('click', function () { openEditDialog(null); });
    if (logoutBtn) logoutBtn.addEventListener('click', function () { localStorage.removeItem('adminSession'); window.location.href = '/admin'; });
    if (dialog) {
      function closeAdminDialog() {
        dialog.classList.remove('open');
        dialog.setAttribute('aria-hidden', 'true');
      }
      dialog.querySelectorAll('[data-close-dialog]').forEach(function (b) {
        b.addEventListener('click', closeAdminDialog);
      });
      dialog.addEventListener('click', function (e) {
        if (e.target === dialog) closeAdminDialog();
      });
    }
    if (dialogForm) {
      var imgZone = dialogForm.querySelector('.img-upload-zone');
      var imgInput = dialogForm.querySelector('.img-upload-zone input[type="file"]');
      var imgPreview = dialogForm.querySelector('.img-preview');
      if (imgZone) {
        imgZone.addEventListener('dragover', function (e) { e.preventDefault(); imgZone.classList.add('border-primary'); });
        imgZone.addEventListener('dragleave', function () { imgZone.classList.remove('border-primary'); });
        imgZone.addEventListener('drop', function (e) {
          e.preventDefault();
          imgZone.classList.remove('border-primary');
          var f = e.dataTransfer.files[0];
          if (f && f.type.startsWith('image/')) {
            var r = new FileReader();
            r.onload = function () { imgPreview.src = r.result; imgPreview.style.display = 'block'; };
            r.readAsDataURL(f);
          }
        });
        imgZone.querySelector('.img-file-btn') && imgZone.querySelector('.img-file-btn').addEventListener('click', function () { imgInput && imgInput.click(); });
        imgZone.querySelector('.img-url-btn') && imgZone.querySelector('.img-url-btn').addEventListener('click', function () {
          var url = prompt('이미지 URL을 입력하세요:');
          if (url) { imgPreview.src = url; imgPreview.style.display = 'block'; }
        });
      }
      if (imgInput) imgInput.addEventListener('change', function () {
        var f = this.files[0];
        if (f) { var r = new FileReader(); r.onload = function () { imgPreview.src = r.result; imgPreview.style.display = 'block'; }; r.readAsDataURL(f); }
      });
      dialogForm.addEventListener('submit', function (e) {
        e.preventDefault();
        var formData = new FormData(dialogForm);
        var imgPreviewEl = dialogForm.querySelector('.img-preview');
        var specsSpans = dialogForm.querySelectorAll('.specs-list .badge span');
        var featuresSpans = dialogForm.querySelectorAll('.features-list .badge span');
        var rawImg = (imgPreviewEl && imgPreviewEl.src) || '';
        var rawPrice = String(formData.get('price') || '').replace(/[^0-9]/g, '');
        var rawDownloadUrl = String(formData.get('downloadUrl') || '').trim();
        var data = {
          name: String(formData.get('name') || '').trim(),
          category: String(formData.get('category') || '').trim(),
          description: String(formData.get('description') || '').trim(),
          detailedDescription: String(formData.get('detailedDescription') || '').trim(),
          code: String(formData.get('code') || '').trim(),
          image: isValidImageUrl(rawImg) ? rawImg : '',
          price: rawPrice === '' ? '0' : rawPrice,
          downloadUrl: safeLinkUrl(rawDownloadUrl) ? rawDownloadUrl : '',
          specs: Array.from(specsSpans).map(function (s) { return s.textContent.trim(); }).filter(Boolean),
          features: Array.from(featuresSpans).map(function (s) { return s.textContent.trim(); }).filter(Boolean),
        };
        if (!data.name || !data.category || !data.description) {
          toast('필수 항목을 입력해주세요.', 'error');
          return;
        }
        var id = dialogForm.dataset.editingId;
        var url = id ? '/api/products/' + id : '/api/products';
        var method = id ? 'PUT' : 'POST';
        api(url, { method: method, body: data })
          .then(function () {
            toast(id ? '제품이 수정되었습니다.' : '제품이 추가되었습니다.');
            if (dialog) { dialog.classList.remove('open'); dialog.setAttribute('aria-hidden', 'true'); }
            loadProducts();
          })
          .catch(function (err) { toast(err.message || '오류가 발생했습니다.', 'error'); });
      });
    }
    loadProducts();
  }

  // === 404 ===
  function init404() {
    var btn = document.getElementById('go-home-btn');
    if (btn) btn.addEventListener('click', function () { window.location.href = '/'; });
  }

  // === 사이드바 (전역) — aria-hidden 보조기술 호환: 닫을 때 포커스를 토글로 이동 후 숨김 ===
  function initSidebar() {
    var toggle = document.getElementById('sidebar-toggle');
    var closeBtn = document.getElementById('sidebar-close-btn');
    var backdrop = document.getElementById('sidebar-backdrop');
    var sidebar = document.getElementById('app-sidebar');
    function setSidebarHidden(hidden) {
      if (sidebar) sidebar.setAttribute('aria-hidden', hidden ? 'true' : 'false');
    }
    function closeSidebar() {
      if (toggle) toggle.focus();
      document.body.classList.remove('sidebar-open');
      setSidebarHidden(true);
    }
    function openSidebar() {
      document.body.classList.add('sidebar-open');
      setSidebarHidden(false);
    }
    function toggleSidebar() {
      var isOpen = document.body.classList.toggle('sidebar-open');
      setSidebarHidden(!isOpen);
      if (!isOpen && toggle) toggle.focus();
    }
    if (toggle) toggle.addEventListener('click', toggleSidebar);
    if (closeBtn) closeBtn.addEventListener('click', closeSidebar);
    if (backdrop) backdrop.addEventListener('click', closeSidebar);
  }

  // === 라우트별 초기화 ===
  initSidebar();
  var path = window.location.pathname;
  if (path === '/' || path === '') initHome();
  else if (path === '/admin') initAdminLogin();
  else if (path === '/admin/dashboard') initAdminDashboard();
  else if (path === '/404' || document.getElementById('not-found-page')) init404();
})();
