#!/usr/bin/env python3
"""
SPL Visual Debugger - Enhanced
Vidokezo vya Udhibiti wa Maonyesho ya Miundo ya Data
"""
import graphviz
from typing import Union, Dict, List, Optional

class Kivizulia:
    def __init__(self):
        self.chati = graphviz.Digraph('AST', format='png',
                                    graph_attr={'rankdir': 'TB', 'bgcolor': '#FFFFF0'},
                                    node_attr={'style': 'filled', 'fillcolor': '#E0FFFF'})
        self.id_ya_node = 0
        self.rangi_za_node = {
            'FunctionDef': '#FFE4B5',
            'PatternMatch': '#98FB98',
            'BinaryOp': '#DDA0DD',
            'FunctionCall': '#87CEEB',
            'default': '#F0F8FF'
        }

    def _unda_node(self, aina: str, maandishi: str) -> str:
        """Unda nodi mpya na rangi inayofaa"""
        kitambulisho = f'n{self.id_ya_node}'
        rangi = self.rangi_za_node.get(aina, self.rangi_za_node['default'])
        lebo = f"{aina}\n{maandishi}" if maandishi else aina
        
        self.chati.node(kitambulisho, lebo, 
                       shape='rectangle' if aina == 'FunctionDef' else 'ellipse',
                       fillcolor=rangi)
        self.id_ya_node += 1
        return kitambulisho

    def _safiri_ast(self, nodi: Union[Dict, List], kitambulisho_mzazi: Optional[str] = None):
        """Safiri muundo wa AST na uunde michoro"""
        if isinstance(nodi, dict):
            aina = nodi.get('aina', 'Haijulikani')
            maudhui = self._fanya_maudhui(nodi)
            kitambulisho = self._unda_node(aina, maudhui)
            
            if kitambulisho_mzazi:
                self.chati.edge(kitambulisho_mzazi, kitambulisho)
                
            for ufunguo, thamani in nodi.items():
                if ufunguo in ['aina', 'thamani', 'jina']:
                    continue
                self._chora_kivinjari(thamani, kitambulisho, ufunguo)

        elif isinstance(nodi, list):
            for kipengele in nodi:
                self._safiri_ast(kipengele, kitambulisho_mzazi)

    def _chora_kivinjari(self, data, kitambulisho_mzazi: str, ufunguo: str):
        """Chora viungo kwa nodi za mtoto"""
        if isinstance(data, dict):
            kitambulisho = self._safiri_ast(data, kitambulisho_mzazi)
            self.chati.edge(kitambulisho_mzazi, kitambulisho, label=ufunguo)
        elif isinstance(data, list):
            for i, kipengele in enumerate(data):
                kitambulisho = self._safiri_ast(kipengele, kitambulisho_mzazi)
                self.chati.edge(kitambulisho_mzazi, kitambulisho, label=f"{ufunguo}[{i}]")
        else:
            kitambulisho = self._unda_node('Thamani', str(data))
            self.chati.edge(kitambulisho_mzazi, kitambulisho, label=ufunguo)

    def _fanya_maudhui(self, nodi: Dict) -> str:
        """Tengeneza maudhui ya nodi kutoka kwa sifa muhimu"""
        vipengele = []
        for ufunguo in ['jina', 'thamani', 'rudisha']:
            if ufunguo in nodi:
                vipengele.append(f"{ufunguo}: {nodi[ufunguo]}")
        return "\n".join(vipengele)

    def onyesha_ast(self, ast: Dict, jina_la_faili: str = "ast") -> str:
        """
        Tengeneza na uonyeshe mchoro wa AST
        
        :param ast: Muundo wa Abstract Syntax Tree
        :param jina_la_faili: Jina la faili la pato (bila kitanzi)
        :return: Njia kamili ya faili iliyotengenezwa
        """
        self.chati = graphviz.Digraph('AST', format='png')  # Reset chati
        self.id_ya_node = 0
        self._safiri_ast(ast)
        
        njia = self.chati.render(filename=jina_la_faili, cleanup=True)
        print(f"🖼  Mchoro umehifadhiwa katika: {njia}")
        return njia

    def onyesha_halisi(self, data: Dict, kina: int = 3) -> str:
        """
        Onyesha muundo wa data kwa kina maalum
        
        :param data: Muundo wa data wa Python
        :param kina: Kina cha uchambuzi
        :return: Njia ya faili
        """
        self.chati = graphviz.Digraph('Data', format='png')
        self.id_ya_node = 0
        self._safiri_halisi(data, kina=kina)
        return self.chati.render(cleanup=True)

    def _safiri_halisi(self, data, kina: int, kitambulisho_mzazi: Optional[str] = None):
        """Safiri muundo wa data wa kawaida"""
        if kina < 0:
            return
            
        aina = type(data).__name__
        kitambulisho = self._unda_node(aina, str(data))
        
        if kitambulisho_mzazi:
            self.chati.edge(kitambulisho_mzazi, kitambulisho)
            
        if isinstance(data, dict):
            for k, v in data.items():
                nodi_mtoto = self._safiri_halisi(v, kina-1, kitambulisho)
                self.chati.edge(kitambulisho, nodi_mtoto, label=str(k))
        elif isinstance(data, (list, tuple)):
            for i, item in enumerate(data):
                nodi_mtoto = self._safiri_halisi(item, kina-1, kitambulisho)
                self.chati.edge(kitambulisho, nodi_mtoto, label=str(i))

if __name__ == '__main__':
    # Mfano wa AST wa kazi ya Fibonacci
    ast_ya_mfano = {
        "aina": "UfafanuziWaKazi",
        "jina": "fib",
        "vigezo": [{"aina": "Kigezo", "jina": "n", "aina_ya_data": "nambari"}],
        "mwili": [
            {
                "aina": "MwendesoWaSampuli",
                "usemi": {"aina": "Kigezo", "jina": "n"},
                "kesi": [
                    {
                        "sampuli": {"aina": "Nambari", "thamani": 0},
                        "mwili": [{"aina": "Nambari", "thamani": 0}]
                    },
                    {
                        "sampuli": {"aina": "Nambari", "thamani": 1},
                        "mwili": [{"aina": "Nambari", "thamani": 1}]
                    }
                ]
            }
        ]
    }

    kivizulia = Kivizulia()
    
    # Oonyesha AST
    kivizulia.onyesha_ast(ast_ya_mfano, "mfano_ast")
    
    # Oonyesha muundo wa data halisi
    data = {'orodha': [1, 2, {'kamusi': 'thamani'}], 'nambari': 42}
    kivizulia.onyesha_halisi(data, kina=2)