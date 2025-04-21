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

       // Tìm kiếm đường theo quận
    $('#street').on('input', function () {
        const query = $(this).val();
        const district = $('#district').val();

        if (district && query.length > 2) {
            $.get(`/search_street_in_district`, { district, query }, function (data) {
                $('#street-suggestions').empty().show();
                data.forEach(street => {
                    $('#street-suggestions').append(`
                        <a class="dropdown-item" href="#" data-street="${street}">
                            ${street}
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
        const street = $(this).data('street');
        $('#street').val(street);
        $('#street-suggestions').hide();
    });

    // Submit form dự đoán
    let allowedStreets = [];

$('#district').change(function () {
    const district = $(this).val();
    if (district) {
        $.get(`/get_streets/${district}`, function (streets) {
            allowedStreets = streets;
        });
    } else {
        allowedStreets = [];
    }
});

$('#predict-form').submit(function (e) {
    e.preventDefault();
    const street = $('#street').val();

    if (!allowedStreets.includes(street)) {
        $('#result').html('Vui lòng chọn đường từ danh sách có sẵn').removeClass('text-success').addClass('text-danger');
        return;
    }

    const formData = {
        district: $('#district').val(),
        ward: $('#ward').val(),
        street: street,
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
            $('#result').html(`Giá nhà dự đoán: ${response.price} tỷ VNĐ`).removeClass('text-danger').addClass('text-success');
            $('#price_level').html(`Phân khúc giá nhà ở: ${response.price_level}`).removeClass('text-danger').addClass('text-success');
            $('#price_range').html(`Giá dao động: ${response.price_range}`).removeClass('text-danger').addClass('text-success');
        },
        error: function (xhr) {
            let errorMsg = 'Có lỗi xảy ra, vui lòng thử lại!';
            if (xhr.responseJSON && xhr.responseJSON.error) {
                errorMsg = xhr.responseJSON.error;
            }
            $('#result').html(errorMsg).removeClass('text-success').addClass('text-danger');
        }
    });
});

});