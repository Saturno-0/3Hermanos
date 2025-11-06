import flet as ft
from modals.modal_crud_producto import show_modal_editar_producto
from modals.modal_pago import show_modal_pago 
from modals.modal_apartado import show_modal_apartado
from modals.modal_corte import show_modal_corte  
from database.manager import obtener_productos
from functools import partial
from datetime import datetime

