$(document).ready(function () {
    // Load wards khi chọn quận
    $('#district').change(function () {
        const district = $(this).val();
        if (district) {
            $.get(`/get_wards/${district}`, function (data) {
                $('#ward').empty().append('<option value="">Chọn phường</option>');
                data.forEach(ward => {
                    $('#ward').append(`<option value="${ward}">${ward}</option>`);
                });
            });
        } else {
            $('#ward').empty().append('<option value="">Chọn phường</option>');
        }
    });

    // Tìm kiếm tên đường
    $('#street').on('input', function () {
        const query = $(this).val();
        if (query.length > 2) {
            $.get(`/search_street/${query}`, function (data) {
                $('#street-suggestions').empty().show();
                data.forEach(item => {
                    $('#street-suggestions').append(`
                        <a class="dropdown-item" href="#" data-district="${item.district}" data-street="${item.street}">
                            ${item.street} (${item.district})
                        </a>
                    `);
                });
            });
        } else {
            $('#street-suggestions').empty().hide();
        }
    });

    // Chọn đường từ gợi ý
    $('#street-suggestions').on('click', '.dropdown-item', function (e) {
        e.preventDefault();
        const district = $(this).data('district');
        const street = $(this).data('street');
        $('#district').val(district);
        $('#street').val(street);
        $('#street-suggestions').hide();

        // Load lại wards cho district
        $('#district').trigger('change');
    });

    // Submit form dự đoán
    $('#predict-form').submit(function (e) {
        e.preventDefault();
        const formData = {
            district: $('#district').val(),
            ward: $('#ward').val(),
            street: $('#street').val(),
            house_type: $('#house_type').val(),
            legal_status: $('#legal_status').val(),
            length: $('#length').val(),
            width: $('#width').val(),
            bedrooms: $('#bedrooms').val(),
            bathrooms: $('#bathrooms').val(),
            floors: $('#floors').val()
        };

        $.ajax({
            url: '/predict',
            type: 'POST',
            data: formData,
            success: function (response) {
                $('#result').html(`Giá nhà dự đoán: ${response.price} tỷ VNĐ`).addClass('text-success');
            },
            error: function () {
                $('#result').html('Có lỗi xảy ra, vui lòng thử lại!').addClass('text-danger');
            }
        });
    });
});