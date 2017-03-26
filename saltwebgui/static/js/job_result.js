$(function () {
            $('.results > li').hide();

            $('div.tags').find('input:checkbox').on('click', function () {
                $('.results > li').hide();
                $('div.tags').find('input:checked').each(function () {
                    $('.results > li.' + $(this).attr('rel')).show();
                });
            });
        });      

$(function () {
            $('.results > li > ul > li').hide();

            $('div.fields').find('input:checkbox').on('click', function () {
                $('.results > li > ul > li').hide();
                $('div.fields').find('input:checked').each(function () {
                    $('.results > li > ul > li.' + $(this).attr('rel')).show();
                });
            });
        });      
