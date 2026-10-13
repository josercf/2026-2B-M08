"""Põe o backend no sys.path: os testes importam main, carteira e interpretacao
como a API importa, sem instalar nada."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
