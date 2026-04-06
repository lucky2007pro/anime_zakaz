(function () {
    function formatBytes(bytes) {
        if (!Number.isFinite(bytes) || bytes <= 0) {
            return '0 B';
        }
        var units = ['B', 'KB', 'MB', 'GB'];
        var idx = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1);
        var val = bytes / Math.pow(1024, idx);
        return val.toFixed(idx === 0 ? 0 : 1) + ' ' + units[idx];
    }

    function initUploadProgress(formSelector) {
        var form = document.querySelector(formSelector);
        if (!form) {
            return;
        }

        var progressWrap = document.getElementById('upload-progress-wrap');
        var progressFill = document.getElementById('upload-progress-fill');
        var progressPercent = document.getElementById('upload-progress-percent');
        var progressText = document.getElementById('upload-progress-text');
        var submitBtn = form.querySelector('button[type="submit"]');
        var uploadInput = form.querySelector('input[type="file"][name="video_file"]');

        var isUploading = false;

        function setProgress(percent, text) {
            if (!progressWrap || !progressFill || !progressPercent || !progressText) {
                return;
            }
            progressWrap.style.display = 'block';
            progressFill.style.width = percent + '%';
            progressPercent.textContent = percent + '%';
            progressText.textContent = text;
        }

        function toggleFormState(disabled) {
            if (submitBtn) {
                submitBtn.disabled = disabled;
                submitBtn.style.opacity = disabled ? '0.7' : '1';
                submitBtn.style.cursor = disabled ? 'not-allowed' : 'pointer';
            }
            if (uploadInput) {
                uploadInput.disabled = disabled;
            }
        }

        window.addEventListener('beforeunload', function (event) {
            if (!isUploading) {
                return;
            }
            event.preventDefault();
            event.returnValue = '';
        });

        form.addEventListener('submit', function (event) {
            event.preventDefault();

            var xhr = new XMLHttpRequest();
            var formData = new FormData(form);
            var startedAt = Date.now();

            isUploading = true;
            toggleFormState(true);
            setProgress(0, 'Yuklash boshlandi...');

            xhr.open('POST', form.action || window.location.href, true);
            xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');

            xhr.upload.onprogress = function (e) {
                if (!e.lengthComputable) {
                    setProgress(0, 'Yuklanmoqda...');
                    return;
                }

                var percent = Math.max(0, Math.min(100, Math.round((e.loaded / e.total) * 100)));
                var elapsedSec = Math.max((Date.now() - startedAt) / 1000, 0.001);
                var speed = e.loaded / elapsedSec;
                setProgress(
                    percent,
                    'Yuklanmoqda: ' + formatBytes(e.loaded) + ' / ' + formatBytes(e.total) + ' (' + formatBytes(speed) + '/s)'
                );
            };

            xhr.onload = function () {
                isUploading = false;
                toggleFormState(false);

                var payload = null;
                try {
                    payload = JSON.parse(xhr.responseText || '{}');
                } catch (err) {
                    payload = null;
                }

                if (xhr.status >= 200 && xhr.status < 300 && payload && payload.ok) {
                    setProgress(100, 'Yuklash yakunlandi. Saqlanmoqda...');
                    window.location.href = payload.redirect_url || window.location.href;
                    return;
                }

                var errText = (payload && payload.error) ? payload.error : 'Yuklashda xatolik yuz berdi.';
                setProgress(0, errText);
                alert(errText);
            };

            xhr.onerror = function () {
                isUploading = false;
                toggleFormState(false);
                setProgress(0, 'Tarmoq xatosi. Internetni tekshirib qayta urinib ko\'ring.');
            };

            xhr.send(formData);
        });
    }

    window.BestMediaUploadProgress = {
        initUploadProgress: initUploadProgress
    };
})();

