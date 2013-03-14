(function ($) {
    var EntradaView = function () {
        var that = this;

        this.produtoCombobox = $('#produto-select').qcombobox({
            url: './?cmd=auto_complete_produto'
        }).data('combobox');
        
        this.produtoCombobox.$element.attr('placeholder', "Produto");
        this.produtoCombobox.$element.addClass('input-xlarge');
        
        this.produtoCombobox.$target.change(function () {
            var produtoId = $(this).val();
            if (produtoId) {
                $('#qtde-container').removeClass('hide');
                
                $.getJSON('.', {cmd: 'get_estoque', produto_id: produtoId}, function (data) {
                    $('#qtde-estoque').text(data.qtde);
                    
                });
            } else {
                $('#qtde-container').addClass('hide');
            }
            
        });
        
        $("#add-produto").click(function (e) {
            that.addProduto();
        });
    };
    
    EntradaView.prototype = {
        constructor: EntradaView,
        addProduto: function () {
            var that = this;
            produtoId = $('#produto-select').val(),
            produtoQtde = $('#produto-qtde').val();

            if (!produtoId) {
                alert('Preencha o produto primeiramente');
                return;
            }

            if (!produtoQtde) {
                alert('Preencha a quantidade do produto primeiramente');
                return;
            }

            this.produtoCombobox.$element.val('');
            this.produtoCombobox.$target.empty;
            this.produtoCombobox.$target.val('');
            this.produtoCombobox.clearTarget();
            $('#produto-qtde').val('');

            $.post('.', {cmd: 'add_produto', 'produto_id': produtoId,
                         produto_qtde: produtoQtde},
                   function (data) {
                       
                       if (!data.added) {
                           $('#response-text').text("Produto não encontrado");
                           return;
                       }

                       $('#response-text').text("Agora temos "+data.total+" unidades do produto "+data.nome);
            });
        }
    };

    $(document).ready(function () {
        window.view = new EntradaView();
    });
})(jQuery);
