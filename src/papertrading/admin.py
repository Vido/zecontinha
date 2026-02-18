from django.contrib import admin
from .models import Trade


@admin.register(Trade)
class TradeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "display_pair",
        "display_qnt",
        "market",
        "periodo",
        "display_quote",
        "display_zscore",
        "display_profit",
        "t_entry",
        "t_exit",
        "is_open",
    )

    list_filter = (
        "market",
        "periodo",
        "t_entry",
        "t_exit",
    )

    search_fields = (
        "user__username",
        "ativo_x",
        "ativo_y",
    )

    readonly_fields = (
        "display_pair",
        "display_qnt",
        "display_quote",
        "display_zscore",
        "display_profit",
        "t_entry",
        "t_exit",
    )

    fieldsets = (
        ("User & Market", {
            "fields": ("user", "market", "periodo")
        }),
        ("Pair", {
            "fields": (
                ("ativo_x", "qnt_x", "entry_x", "exit_x"),
                ("ativo_y", "qnt_y", "entry_y", "exit_y"),
            )
        }),
        ("Computed", {
            "fields": (
                "display_pair",
                "display_qnt",
                "display_quote",
                "display_zscore",
                "display_profit",
            )
        }),
        ("Dates", {
            "fields": ("t_entry", "t_exit")
        }),
        ("Advanced", {
            "classes": ("collapse",),
            "fields": ("model_params", "beta_rotation"),
        }),
    )

    def is_open(self, obj):
        return obj.is_open()

    is_open.boolean = True
    is_open.short_description = "Open"
