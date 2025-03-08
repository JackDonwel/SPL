#!/usr/bin/env python3
"""
SPL Type Checker - Enhanced
"""
from dataclasses import dataclass
from typing import Dict, List, Optional, Union


class TypeChecker:
    """SPL Type Validation System"""
    def __init__(self):
        self.type_map = {
            'nambari': float,
            'neno': str,
            'orodha': list,
            'kamusi': dict
        }
    
    def check(self, value, expected_type: str):
        """Verify value matches expected SPL type"""
        py_type = self.type_map.get(expected_type.lower())
        if not py_type:
            raise TypeError(f"Undefined type: {expected_type}")
        
        if not isinstance(value, py_type):
            raise TypeError(f"Expected {expected_type}, got {type(value).__name__}")

class KosaAina(Exception):
    """Custom type error with Swahili messages and location info"""
    def __init__(self, ujumbe: str, eneo: Optional[Dict] = None):
        super().__init__(f"Kosa la Aina{' ' + self.format_eneo(eneo) if eneo else ''}: {ujumbe}")
        self.eneo = eneo

    @staticmethod
    def format_eneo(eneo: Dict) -> str:
        return f"(mstari {eneo['start_line']}, safu {eneo['start_col']})" if eneo else ""

@dataclass
class Aina:
    """Base type representation"""
    jina: str
    eneo: Optional[Dict] = None

class AinaKamili(Aina):
    """Concrete type like int, float"""
    pass

class AinaKazi(Aina):
    """Function type"""
    def __init__(self, param: List[Aina], kurudi: Aina, eneo: Dict):
        super().__init__("kazi", eneo)
        self.param = param
        self.kurudi = kurudi

class AinaOrodha(Aina):
    """List type"""
    def __init__(self, ndani: Aina, eneo: Dict):
        super().__init__("orodha", eneo)
        self.ndani = ndani

class MazingiraAina:
    """Type environment with Swahili named methods"""
    def __init__(self, mzazi=None):
        self.mzazi = mzazi
        self.aina = {}

    def weka(self, jina: str, aina: Aina):
        self.aina[jina] = aina

    def pata(self, jina: str) -> Aina:
        if jina in self.aina:
            return self.aina[jina]
        if self.mzazi:
            return self.mzazi.pata(jina)
        raise KosaAina(f"Kigezo '{jina}' hakijafafanuliwa")

    def fungua_kitundu(self) -> 'MazingiraAina':
        return MazingiraAina(self)

class KihakikiAina:
    def __init__(self):
        self.mazingira = MazingiraAina()
        self.aina_ya_msingi = {
            'int': AinaKamili('int'),
            'float': AinaKamili('float'),
            'str': AinaKamili('str'),
            'any': AinaKamili('any'),
            'Task': AinaKamili('Task')
        }

    def hakiki(self, ast: List[Dict]) -> List[Aina]:
        matokeo = []
        for kitu in ast:
            matokeo.append(self.tembelea(kitu))
        return matokeo

    def tembelea(self, kitu: Dict) -> Aina:
        njia = getattr(self, f"tembelea_{kitu['type']}", None)
        if not njia:
            raise KosaAina(f"Hakuna uhandisi wa aina kwa {kitu['type']}", kitu.get('loc'))
        return njia(kitu)

    def tembelea_Number(self, kitu: Dict) -> Aina:
        thamani = kitu['value']
        aina = 'float' if isinstance(thamani, float) else 'int'
        return AinaKamili(aina, kitu.get('loc'))

    def tembelea_String(self, kitu: Dict) -> Aina:
        return AinaKamili('str', kitu.get('loc'))

    def tembelea_Var(self, kitu: Dict) -> Aina:
        jina = kitu['name']
        try:
            return self.mazingira.pata(jina)
        except KosaAina as k:
            raise KosaAina(f"Kigezo '{jina}' hakijafafanuliwa", kitu.get('loc')) from k

    def tembelea_Assignment(self, kitu: Dict) -> Aina:
        jina = kitu['name']
        aina_ya_thamani = self.tembelea(kitu['value'])
        self.mazingira.weka(jina, aina_ya_thamani)
        return aina_ya_thamani

    def tembelea_BinaryOp(self, kitu: Dict) -> Aina:
        op = kitu['operator']
        aina_kushoto = self.tembelea(kitu['left'])
        aina_kulia = self.tembelea(kitu['right'])
        eneo = kitu.get('loc')

        # Ukaguzi wa aina kwa kila kiendeshazi
        if op in {'+', '-', '*', '/'}:
            if not self.aina_linganipo(aina_kushoto, aina_kulia, ['int', 'float']):
                raise KosaAina(f"Kiendeshazi '{op}' haifanyi kazi kwa {aina_kushoto.jina} na {aina_kulia.jina}", eneo)
            return self.aina_ya_matokeo(aina_kushoto, aina_kulia)
        
        if op in {'==', '!=', '<', '>', '<=', '>='}:
            if not self.aina_linganipo(aina_kushoto, aina_kulia):
                raise KosaAina(f"Kulinganisha '{op}' haifanyi kazi kwa {aina_kushoto.jina} na {aina_kulia.jina}", eneo)
            return AinaKamili('int', eneo)
        
        if op in {'&&', '||'}:
            if aina_kushoto.jina != 'int' or aina_kulia.jina != 'int':
                raise KosaAina(f"Kiendeshazi '{op}' inahitaji nambari kamili", eneo)
            return AinaKamili('int', eneo)
        
        raise KosaAina(f"Kiendeshazi '{op}' haijatangamana", eneo)

    def aina_linganipo(self, a: Aina, b: Aina, ruhusa: List[str] = None) -> bool:
        """Angalia kama aina zinaweza kufanywa kazi pamoja"""
        if ruhusa and (a.jina not in ruhusa or b.jina not in ruhusa):
            return False
        return a.jina == b.jina or 'any' in {a.jina, b.jina}

    def aina_ya_matokeo(self, a: Aina, b: Aina) -> Aina:
        """Amua aina ya matokeo ya kiendeshazi"""
        if a.jina == 'float' or b.jina == 'float':
            return AinaKamili('float')
        return AinaKamili('int')

    def tembelea_FunctionDef(self, kitu: Dict) -> Aina:
        jina = kitu['name']
        eneo = kitu.get('loc')
        
        # Pata aina za vigezo
        aina_param = [self.tafsiri_aina(p.get('type', 'any')) for p in kitu['params']]
        
        # Pata aina ya kurudi
        aina_kurudi = self.tafsiri_aina(kitu.get('return_type', 'any'))
        
        # Fungua mazingira mapya
        mazingira_ya_kazi = self.mazingira.fungua_kitundu()
        for param, aina in zip(kitu['params'], aina_param):
            mazingira_ya_kazi.weka(param['name'], aina)
        
        # Badili mazingira na uhakiki mwili
        mazingira_ya_awali = self.mazingira
        self.mazingira = mazingira_ya_kazi
        
        aina_mwili = AinaKamili('any')
        for stmt in kitu['body']:
            aina_mwili = self.tembelea(stmt)
        
        self.mazingira = mazingira_ya_awali
        
        # Uhifadhi aina ya kazi
        aina_kazi = AinaKazi(aina_param, aina_kurudi, eneo)
        self.mazingira.weka(jina, aina_kazi)
        
        # Angalia ufanisi wa aina ya kurudi
        if not self.aina_linganipo(aina_mwili, aina_kurudi):
            raise KosaAina(f"Aina ya kurudi {aina_mwili.jina} hailingani na {aina_kurudi.jina}", eneo)
        
        return aina_kazi

    def tafsiri_aina(self, jina_aina: str) -> Aina:
        """Badili jina la aina kuwa kitu cha Aina"""
        if jina_aina.startswith('orodha['):
            ndani = jina_aina[7:-1]
            return AinaOrodha(self.tafsiri_aina(ndani), {})
        return self.aina_ya_msingi.get(jina_aina, AinaKamili(jina_aina))

    def tembelea_FunctionCall(self, kitu: Dict) -> Aina:
        aina_kazi = self.tembelea(kitu['function'])
        eneo = kitu.get('loc')
        
        if not isinstance(aina_kazi, AinaKazi):
            raise KosaAina("Huwezi kuita kitu ambacho si kazi", eneo)
        
        # Pata aina za hoja
        aina_hoja = [self.tembelea(arg) for arg in kitu['args']]
        
        # Linganisha na aina za vigezo
        if len(aina_hoja) != len(aina_kazi.param):
            raise KosaAina(f"Idadi ya hoja si sahihi: {len(aina_hoja)} badala ya {len(aina_kazi.param)}", eneo)
            
        for hoja, param in zip(aina_hoja, aina_kazi.param):
            if not self.aina_linganipo(hoja, param):
                raise KosaAina(f"Aina ya hoja '{hoja.jina}' hailingani na '{param.jina}'", eneo)
        
        return aina_kazi.kurudi

    def tembelea_Print(self, kitu: Dict) -> Aina:
        # Chapisha inaruhusu aina zozote
        self.tembelea(kitu['value'])
        return AinaKamili('none', kitu.get('loc'))

    def tembelea_PatternMatch(self, kitu: Dict) -> Aina:
        aina_ya_linganisho = self.tembelea(kitu['expression'])
        aina_matokeo = None
        
        for kesi in kitu['cases']:
            # Hakiki muundo
            muundo = kesi['pattern']
            if muundo['type'] == 'Literal':
                if not self.aina_linganipo(aina_ya_linganisho, self.tembelea(muundo)):
                    raise KosaAina(f"Muundo {muundo['value']} haufanani na {aina_ya_linganisho.jina}", kesi.get('loc'))
            elif muundo['type'] == 'TypedPattern':
                aina_ya_muundo = self.tafsiri_aina(muundo['annotation'])
                if not self.aina_linganipo(aina_ya_linganisho, aina_ya_muundo):
                    raise KosaAina(f"Muundo {aina_ya_muundo.jina} haufanani na {aina_ya_linganisho.jina}", kesi.get('loc'))
            
            # Hakiki mwili wa kesi
            for stmt in kesi['body']:
                aina_kesi = self.tembelea(stmt)
                if aina_matokeo is None:
                    aina_matokeo = aina_kesi
                elif not self.aina_linganipo(aina_matokeo, aina_kesi):
                    aina_matokeo = AinaKamili('any')
        
        return aina_matokeo or AinaKamili('none')

    def tembelea_Spawn(self, kitu: Dict) -> Aina:
        for stmt in kitu['body']:
            self.tembelea(stmt)
        return AinaKamili('Task', kitu.get('loc'))

if __name__ == '__main__':
    # Jaribio la kuhakiki aina
    ast_mfano = [
        {
            "type": "FunctionDef",
            "name": "ongeza",
            "params": [{"name": "a", "type": "int"}, {"name": "b", "type": "int"}],
            "return_type": "int",
            "body": [
                {"type": "BinaryOp", "operator": "+", 
                 "left": {"type": "Var", "name": "a", "loc": {"start_line": 2}},
                 "right": {"type": "Var", "name": "b", "loc": {"start_line": 2}},
                 "loc": {"start_line": 2}}
            ],
            "loc": {"start_line": 1}
        },
        {
            "type": "FunctionCall",
            "function": {"type": "Var", "name": "ongeza"},
            "args": [
                {"type": "Number", "value": 5},
                {"type": "String", "value": "3"}
            ],
            "loc": {"start_line": 4}
        }
    ]

    hakiki = KihakikiAina()
    try:
        matokeo = hakiki.hakiki(ast_mfano)
        print("Hakiki ya Aina Imefanikiwa!")
    except KosaAina as k:
        print(k)