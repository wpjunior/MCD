$(document).ready(function () {
    var OrcamentoView = function () {
        var that = this;

        this.produtoCombobox = $('#produto-select').qcombobox({
            url: './?cmd=auto_complete_produto'
        }).data('combobox');

        this.produtoCombobox.$element.addClass('input-xlarge');
        this.produtoCombobox.$target.change(function () {
            var produtoId = $(this).val();
            if (produtoId) {
                $('#produto-container').removeClass('hide');

                $.getJSON('.', {cmd: 'get_valores', produto_id: produtoId}, function (data) {
                    $('#id_preco_compra').val(data.valor_compra).trigger('keyup');
                    $('#id_preco_venda').val(data.valor_venda).trigger('keyup');
                });

            } else {
                $('#produto-container').addClass('hide');
            }
            
        });
        $('input.money').priceFormat({
            prefix: 'R$ ',
            centsSeparator: ',',
            thousandsSeparator: '.'
        });

        $('#add-produto').click(function (e) {
            e.preventDefault();
            that.addProduto();
            return false;
        });

        $('#clear-produtos').click(function (e) {
            e.preventDefault();
            $.post('.', {cmd: 'clear_items'}, function () {
                that.preview();
            });

            return false;
        });

        $('#preview').on('click', 'a.remove-item', function (e) {
            e.preventDefault();
            var id = $(this).parents('tr').attr('rel');
            
            $.post('.', {cmd: 'remove_item', id: id}, function () {
                that.preview();
            });

            return false;
        });

        $("#id_cond_pagto").change(function () {
            that.preview();
        });

        $('#print-orcamento').click(function (e) {
            e.preventDefault();
            
            var data = {
                cliente: $('#id_cliente').val(),
                telefone: $('#id_telefone').val(),
                endr: $('#id_endr').val(),
                cond_pagto: $('#id_cond_pagto').val(),
                cmd: 'print_orcamento'
            }

            window.location = './?'+$.param(data);
        });

        this.preview();
    };

    OrcamentoView.prototype = {
        constructor: OrcamentoView,
        addProduto: function () {
            var that = this,
            data= this.getData();

            if (!this.validateData(data))
                return;

            $.post('.', _.extend(data, {
                cmd: 'add_produto'}), function (resp) {
                    that.clearForm();
                    that.preview();
                });
        },
        clearForm: function () {
            this.produtoCombobox.$element.val('');
            this.produtoCombobox.$target.empty;
            this.produtoCombobox.$target.val('');
            this.produtoCombobox.clearTarget();
            $('#id_qtde').val('1')
            $('#produto-container').addClass('hide');
        },
        validateData: function (data) {
            if (!data.produto) {
                var e = $('#produto-select').parent().find('input');
                e.tooltip({
                    title: "Campo obrigatório",
                    trigger: 'manual',
                    placement: 'top',
                    container: e.parent()
                });
                e.tooltip('show');

                var tooltip = e.data('tooltip');

                e.one('change', function () {
                    if (tooltip && tooltip.$tip)
                        tooltip.$tip.remove();
                });

                e.one('keyup', function () {
                    if (tooltip && tooltip.$tip)
                        tooltip.$tip.remove();
                });

                return false;
            }
            
            return true;
        },
        getData: function () {
            return {
                qtde: $('#id_qtde').val(),
                produto: $('#produto-select').val(),
                preco_venda: $('#id_preco_venda').val()
            };
            
        },
        preview: function () {
            $.get('.', {'cmd': 'preview_orcamento',
                        'cond_pagto': $("#id_cond_pagto").val()}, function (html) {
                            // previsualiza
                            $('#preview').html(html);
                        });
        }
    };
    
    window.view = new OrcamentoView();
});
