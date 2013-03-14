(function($) {
    var ConsignacaoView = function () {
        var that = this;

        this.table = $("#list table").listbuilder({
            iDisplayLength: 50
        });

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

        $('#post-delete').click(function (e) {
            e.preventDefault();

            var id = that.table.getRowSelected();
                
            $.post('.', {cmd: 'remove_item', id: id}, function (data) {
                if (!data.removed)
                    alert("Item não removido");

                that.table.reload();
            });

            return false;
        });
        $('#post-clean').click(function (e) {
            if (!confirm("Deseja limpar todos os produtos da consigação?")) return;
            $.post('.', {cmd: 'clear_items'}, function (data) {
                that.table.reload();
            });
        });
    }

    ConsignacaoView.prototype = {
        constructor: ConsignacaoView,
        addProduto: function () {
            var that = this;
            val = $('#produto-select').val();

            if (!val) {
                alert('Preencha o produto primeiramente');
                return;
            }

            this.produtoCombobox.$element.val('');
            this.produtoCombobox.$target.empty;
            this.produtoCombobox.$target.val('');
            this.produtoCombobox.clearTarget();

            $.post('.', {cmd: 'add_produto', 'produto_id': val}, function (data) {
                if (!data.added)
                    alert("Produto não encontrado");

                that.table.reload();
            });
        }
    }

    $(document).ready(function () {
        window.view = new ConsignacaoView();
    });
})(jQuery);
