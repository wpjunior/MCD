(function($) {
    var Consig = function () {
        this._init();
    }

    Consig.prototype = {
        _init: function () {
            var me = this;
            this.table= $("table.display").listbuilder({iDisplayLength: 50});
            $("#produto_cod").keypress(function (e) {
                var code = (e.keyCode ? e.keyCode : e.which);
                if(code == 13) {
                    me.addProduto();
                }
            }).autocomplete({
		source: "./?cmd=auto_complete",
		minLength: 2,
	    });

            $("#add_produto").click(function (e) {
                me.addProduto();
            });

            $('#post-delete').click(function (e) {
                e.preventDefault();

                var id = me.table.getRowSelected();
                
                $.post('.', {'remove_produto': id}, function (data) {
                    if (!data.removed)
                        alert("Produto não removido");
                    me.table.reload();
                });

                return false;
            });
            $('#post-clean').click(function (e) {
                if (!confirm("Deseja limpar todos os produtos da consigação?")) return;
                $.post('.', {'clear_produtos': 1}, function (data) {
                    me.table.reload();
                });
            });
        },
        addProduto: function () {
            var me = this;
            val = $("#produto_cod").val();
            $("#produto_cod").val('');

            $.post('.', {'add_produto': val}, function (data) {
                if (!data.added)
                    alert("Produto não encontrado");

                me.table.reload();
            });
        }
    }

    $(document).ready(function (e) {
        c = new Consig();
    });
})(jQuery);