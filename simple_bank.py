# -*- coding: utf-8 -*-
"""Simple Bank - Módulo Principal v1.0

Um projeto de console interativo que simula as operações essenciais de um sistema
bancário, construído com foco em código limpo e na aplicação prática dos
princípios da Programação Orientada a Objetos.

Examples:
    O exemplo abaixo demonstra o uso programático das classes de modelo,
    independente da interface de console, para ilustrar a lógica de negócio.

    ::

        # 1. Criação do Cliente e da Conta Corrente
        cliente_joao = Cliente(nome="João da Silva", cpf="123.456.789-00")
        conta_joao = ContaCorrente(numero=1, cliente=cliente_joao)
        cliente_joao.adicionar_conta(conta_joao)

        # 2. Realização de um Depósito
        transacao_deposito = Deposito(1000.0)
        cliente_joao.realizar_transacao(conta_joao, transacao_deposito)
        # O saldo da conta_joao agora é 1000.0

        # 3. Realização de um Saque
        transacao_saque = Saque(150.0)
        cliente_joao.realizar_transacao(conta_joao, transacao_saque)
        # O saldo da conta_joao agora é 850.0

        # 4. Visualização do saldo e histórico
        print(f"Saldo final da conta de {conta_joao.cliente.nome}: R$ {conta_joao.saldo:.2f}")
        for data, transacao in conta_joao.historico.transacoes:
            print(f"- {data.strftime('%Y-%m-%d %H:%M')}: {type(transacao).__name__} de R$ {transacao.valor:.2f}")

Attributes:
    COR_VERDE (str): Código de escape ANSI para a cor verde no terminal.
    COR_VERMELHA (str): Código de escape ANSI para a cor vermelha.
    COR_AMARELA (str): Código de escape ANSI para a cor amarela.
    COR_AZUL (str): Código de escape ANSI para a cor azul.
    NEGRITO (str): Código de escape ANSI para o estilo de texto em negrito.
    RESET_COR (str): Código de escape ANSI para resetar a formatação de texto.

Author:
    Victor Neves - github.com/voaneves

Version:
    1.0

License:
    MIT
"""

import logging
import os
import sys
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional, Tuple

# --- Configuração de Logging ---
# (O restante do código permanece o mesmo)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='banco.log',
    filemode='a'
)

# --- Camada de Visão (View/UI) ---
COR_VERDE = '\033[92m'
COR_VERMELHA = '\033[91m'
COR_AMARELA = '\033[93m'
COR_AZUL = '\033[94m'
NEGRITO = '\033[1m'
RESET_COR = '\033[0m'


def limpar_tela():
    """Limpa a tela do console, compatível com Windows, Linux e macOS."""
    os.system('cls' if os.name == 'nt' else 'clear')


def exibir_mensagem(msg: str, sucesso: bool = True):
    """Exibe uma mensagem de status formatada com cores.

    Args:
        msg (str): A mensagem a ser exibida.
        sucesso (bool, optional): Define a cor da mensagem.
            Verde para sucesso, vermelho para falha. Padrão é True.
    """
    cor = COR_VERDE if sucesso else COR_VERMELHA
    print(f"\n{cor}{msg}{RESET_COR}")


def pausar_e_limpar():
    """Pausa a execução até o usuário pressionar Enter e depois limpa a tela."""
    input(f"\n{COR_AMARELA}Pressione Enter para continuar...{RESET_COR}")
    limpar_tela()


# --- Camada de Modelo (Model) ---

class Transacao(ABC):
    """Classe base abstrata para todas as transações financeiras.

    Define um contrato para que todas as transações tenham um valor e
    um método para serem registradas em uma conta.
    """

    @property
    @abstractmethod
    def valor(self) -> float:
        """float: O valor monetário da transação."""
        pass

    @abstractmethod
    def registrar(self, conta: 'Conta') -> bool:
        """Registra a transação na conta especificada.

        Args:
            conta (Conta): A instância da conta onde a transação será aplicada.

        Returns:
            bool: True se a transação for registrada com sucesso, False caso contrário.
        """
        pass


class Saque(Transacao):
    """Representa uma transação de saque.

    Attributes:
        _valor (float): O valor a ser sacado.
    """

    def __init__(self, valor: float):
        self._valor = valor

    @property
    def valor(self) -> float:
        return self._valor

    def registrar(self, conta: 'Conta') -> bool:
        """Registra o saque na conta após validar as regras de negócio.

        Invoca o método `sacar` da conta e, se bem-sucedido, adiciona-se ao
        histórico de transações.

        Args:
            conta (Conta): A conta da qual o valor será sacado.

        Returns:
            bool: True se o saque for efetuado, False caso contrário.
        """
        sucesso_transacao = conta.sacar(self.valor)
        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)
            return True
        return False


class Deposito(Transacao):
    """Representa uma transação de depósito.

    Attributes:
        _valor (float): O valor a ser depositado.
    """

    def __init__(self, valor: float):
        self._valor = valor

    @property
    def valor(self) -> float:
        return self._valor

    def registrar(self, conta: 'Conta') -> bool:
        """Registra o depósito na conta.

        Invoca o método `depositar` da conta e, se bem-sucedido, adiciona-se
        ao histórico de transações.

        Args:
            conta (Conta): A conta na qual o valor será depositado.

        Returns:
            bool: True se o depósito for efetuado, False caso contrário.
        """
        sucesso_transacao = conta.depositar(self.valor)
        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)
            return True
        return False


class Historico:
    """Armazena e gerencia o histórico de transações de uma conta.

    Attributes:
        _transacoes (list): Uma lista de tuplas, onde cada tupla contém
            a data/hora e a instância da transação.
    """


    def __init__(self):
        """Inicializa um histórico de transações vazio."""
        self._transacoes: List[Tuple[datetime, Transacao]] = []

    @property
    def transacoes(self) -> List[Tuple[datetime, Transacao]]:
        """list: Uma cópia da lista de transações para evitar mutações externas."""
        return self._transacoes[:]

    def adicionar_transacao(self, transacao: Transacao):
        """Adiciona uma nova transação ao histórico.

        A transação é armazenada com o timestamp atual e um log é registrado.

        Args:
            transacao (Transacao): A instância da transação a ser adicionada.
        """
        self._transacoes.append((datetime.now(), transacao))
        logging.info(
            f"Transação registrada: {type(transacao).__name__} de R$ {transacao.valor:.2f}"
        )


class Conta:
    """Classe que representa uma conta bancária de um cliente.

    Esta classe serve como base para tipos de contas mais específicos.

    Attributes:
        _saldo (float): O saldo atual da conta.
        _numero (int): O número único que identifica a conta.
        _agencia (str): O número da agência, fixo em "0001".
        _cliente (Cliente): A instância do cliente proprietário da conta.
        _historico (Historico): O objeto que gerencia o histórico de transações.
    """

    def __init__(self, numero: int, cliente: 'Cliente'):
        """Inicializa uma instância de Conta.

        Args:
            numero (int): O número da conta.
            cliente (Cliente): O cliente associado a esta conta.
        """
        self._saldo: float = 0.0
        self._numero: int = numero
        self._agencia: str = "0001"
        self._cliente: 'Cliente' = cliente
        self._historico: Historico = Historico()

    @property
    def saldo(self) -> float:
        """float: Saldo atual da conta."""
        return self._saldo

    @property
    def numero(self) -> int:
        """int: Número da conta."""
        return self._numero

    @property
    def agencia(self) -> str:
        """str: Número da agência."""
        return self._agencia

    @property
    def cliente(self) -> 'Cliente':
        """Cliente: Objeto cliente associado à conta."""
        return self._cliente

    @property
    def historico(self) -> Historico:
        """Historico: Histórico de transações da conta."""
        return self._historico

    @classmethod
    def nova_conta(cls, cliente: 'Cliente', numero: int) -> 'Conta':
        """Método de fábrica para criar uma nova instância de conta.

        Args:
            cliente (Cliente): O cliente para o qual a conta será criada.
            numero (int): O número a ser atribuído à nova conta.

        Returns:
            Conta: Uma nova instância da classe Conta.
        """
        return cls(numero, cliente)

    def sacar(self, valor: float) -> bool:
        """Realiza um saque na conta.

        Valida se o valor do saque é positivo e se há saldo suficiente.
        As regras de limite são implementadas nas subclasses.

        Args:
            valor (float): O valor a ser sacado.

        Returns:
            bool: True se o saque for bem-sucedido, False caso contrário.
        """
        if valor <= 0:
            logging.warning("Tentativa de saque com valor não positivo.")
            return False
        if self._saldo < valor:
            logging.warning("Tentativa de saque com saldo insuficiente.")
            return False

        self._saldo -= valor
        return True

    def depositar(self, valor: float) -> bool:
        """Realiza um depósito na conta.

        Valida se o valor do depósito é positivo.

        Args:
            valor (float): O valor a ser depositado.

        Returns:
            bool: True se o depósito for bem-sucedido, False caso contrário.
        """
        if valor <= 0:
            logging.warning("Tentativa de depósito com valor não positivo.")
            return False

        self._saldo += valor
        return True


class ContaCorrente(Conta):
    """Representa uma conta corrente, herdando de Conta.

    Adiciona regras de negócio específicas para saques, como limite de valor
    por operação e um número máximo de saques diários.

    Attributes:
        _limite (float): O valor máximo permitido por saque.
        _limite_saques (int): O número máximo de saques permitidos por dia.
    """

    def __init__(self, numero: int, cliente: 'Cliente', limite: float = 500.0,
                 limite_saques: int = 3):
        """Inicializa uma instância de ContaCorrente.

        Args:
            numero (int): O número da conta.
            cliente (Cliente): O cliente associado a esta conta.
            limite (float, optional): O limite de valor por saque. Padrão 500.0.
            limite_saques (int, optional): O limite de quantidade de saques
                diários. Padrão 3.
        """
        super().__init__(numero, cliente)
        self._limite: float = limite
        self._limite_saques: int = limite_saques

    def sacar(self, valor: float) -> bool:
        """Sobrescreve o método `sacar` para aplicar regras da conta corrente.

        Antes de chamar o método da classe pai, este método valida se o valor
        do saque excede o limite por operação e se o número de saques diários
        foi atingido.

        Args:
            valor (float): O valor a ser sacado.

        Returns:
            bool: True se o saque for bem-sucedido, False caso contrário.
        """
        saques_hoje = len([
            transacao for _, transacao in self.historico.transacoes
            if isinstance(transacao, Saque) and
