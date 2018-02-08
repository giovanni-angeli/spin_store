# -*- coding: utf-8 -*-
from django.conf.urls import include, url
# ~ from alfalib.navigator.page import Pages
from apps.kiosk.views import main
import apps.kiosk.ajax as ajax


urlpatterns = [
    
    # ~ 'apps.kiosk',

    # Kiosk views
    url(r'^$', main, name='main'),
    url(r'^j/status/$', ajax.status, name='status'),
    url(r'^j/status/dismiss/$', ajax.status_dismiss, name='status-dismiss'),

    #      pages
    # ~ url(r'^page/home/$', Pages.get_page('kiosk.home').ajax, name='home'),
    # ~ url(r'^page/select_color/$', Pages.get_page('kiosk.select_color').ajax, name='select_color'),
    # ~ url(r'^page/confirm_selection/$', Pages.get_page('kiosk.confirm_selection').ajax, name='confirm_selection'),
    # ~ url(r'^page/progress_bar/$', Pages.get_page('kiosk.progress_bar').ajax, name='progress_bar'),
    # ~ url(r'^page/dispensed/$', Pages.get_page('kiosk.dispensed').ajax, name='dispensed'),

    # ~ url(r'^j/colors/$', 'ajax.colors', name='colors'),
    # ~ url(r'^j/set_language/(?P<lang_code>\w+)/$', 'ajax.set_language', name='set_language'),

    url(r'^j/shutter-message/$', ajax.shutter_message, name='shutter-message'),
    url(r'^j/label-busy/$', ajax.label_busy, name='label-busy'),
    url(r'^j/color-available/$', ajax.color_available, name='color-available'),

    url(r'^j/payment-credit/$', ajax.payment_credit, name='payment-credit'),
    url(r'^j/payment-charge/$', ajax.payment_charge, name='payment-charge'),
    url(r'^j/payment-collect/$', ajax.payment_collect, name='payment-collect'),
    url(r'^j/payment-refund/$', ajax.payment_refund, name='payment-refund'),
    url(r'^j/payment-enable/$', ajax.payment_enable, name='payment-enable'),
    url(r'^j/payment-disable/$', ajax.payment_disable, name='payment-disable'),

    # ~ # Kiosk on-board diagnostics view
    # ~ url(r'^diagnostics/$', 'diagnostics.diag_main', name='diagnostics-main'),
    # ~ url(r'^diagnostics/auth/$', 'diagnostics.diag_auth', name='diagnostics-auth'),
    # ~ url(r'^diagnostics/exit/$', 'diagnostics.diag_exit', name='diagnostics-exit'),
    # ~ url(r'^diagnostics/reset/$', 'diagnostics.diag_reset', name='diagnostics-reset'),

    # ~ # AJAX helpers
    # ~ url(r'^j/diagnostics/status', 'diagnostics.diagnostics_status', name='diagnostics-status'),
    # ~ url(r'^j/diagnostics/auto-purge', 'diagnostics.diagnostics_auto_purge', name='diagnostics-auto-purge'),

    # ~ url(r'^j/circuit/(\d+)/refill$', 'diagnostics.diagnostics_circuit_refill', name='diagnostics-circuit-refill'),
    # ~ url(r'^j/circuit/(\d+)/manual-purge', 'diagnostics.diagnostics_manual_purge', name='diagnostics-circuit-manual-purge'),
    # ~ url(r'^j/circuit/(\d+)/purge-volume', 'diagnostics.diagnostics_circuit_purge_volume',
        # ~ name='diagnostics-circuit-purge-volume'),
    # ~ url(r'^j/circuit/(\d+)/levels', 'diagnostics.diagnostics_circuit_levels',
        # ~ name='diagnostics-circuit-levels'),
    # ~ url(r'^j/circuit/(\d+)/settings', 'diagnostics.diagnostics_circuit_settings',
        # ~ name='diagnostics-circuit-settings'),
    # ~ url(r'^j/circuit/(\d+)/setup-recirculation', 'diagnostics.diagnostics_setup_recirculation', name='diagnostics-setup-recirculation'),
    # ~ url(r'^j/circuit/(\d+)/control-recirculation', 'diagnostics.diagnostics_control_recirculation', name='diagnostics-control-recirculation'),
    # ~ url(r'^j/circuit/(\d+)/control-stirring', 'diagnostics.diagnostics_control_stirring', name='diagnostics-control-stirring'),

    # ~ # Diagnostics pages
    # ~ url(r'^j/page_main/$', 'diagnostics.page_main', name='page_main'),
    # ~ url(r'^j/page_main/footer/$', 'diagnostics.page_main_footer', name='page_main_footer'),

    # ~ url(r'^j/page_carriage/$', 'diagnostics.page_carriage', name='page_carriage'),
    # ~ url(r'^j/page_carriage/footer/$', 'diagnostics.page_carriage_footer', name='page_carriage_footer'),

    # ~ url(r'^j/circuit/(\d+)/$', 'diagnostics.page_circuit', name='page_circuit'),
    # ~ url(r'^j/circuit/(\d+)/footer/$', 'diagnostics.page_circuit_footer', name='page_circuit_footer'),

    # ~ url(r'^sample-table-circuit/$', 'views.sample_table_circuit', name='sample_table_circuit'),
]
