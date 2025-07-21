# -*- coding: utf-8 -*-
"""Simple Bank - Módulo Principal v2.0

Esta versão evolui o sistema bancário, introduzindo exceções customizadas para
um desacoplamento total entre a lógica de negócio e a interface, validação de
entrada de dados para maior robustez e uma sintaxe de função mais explícita com
argumentos positional-only.

Examples:
    O exemplo abaixo demonstra o uso programático e o tratamento de exceções,
    que é uma das principais melhorias desta versão.

    ::

        # 1. Setup inicial
        cliente = Cliente(nome="Ana Paula", cpf="11122233344")
        conta = ContaCorrente(numero=1, cliente=cliente)
        cliente.adicionar_conta(conta)

        # 2. Transação bem-sucedida
        try:
            deposito = Deposito(2000.0)
            cliente.realizar_transacao(conta, deposito)
            print(f"Depósito realizado com sucesso! Saldo: {conta.saldo:.2f}")
        except ErroBancario as e:
            print(e)

        # 3. Tentativa de saque com saldo insuficiente (tratando a exceção)
        try:
            saque_alto = Saque(2500.0)
            cliente.realizar_transacao(conta, saque_alto)
        except SaldoInsuficienteError as e:
            print(f"Erro capturado: {e.message}")


Attributes:
    COR_VERDE (str): Código de escape ANSI para a cor verde no terminal.
    COR_VERMELHA (str): Código de escape ANSI para a cor vermelha.
    COR_AMARELA (str): Código de escape ANSI para a cor amarela.
    COR_AZUL (str): Código de escape ANSI para a cor azul.
    NEGRITO (str): Código de escape ANSI для o estilo de texto em negrito.
    RESET_COR (str): Código de escape ANSI para resetar a formatação de texto.

Author:
    Victor Neves - github.com/voaneves

Version:
    2.0

License:
    MIT
"""

import logging
import os
import sys
import textwrap
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional, Tuple

# --- Configuração de Logging ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='banco.log',
    filemode='a'
)

# --- Camada de Visão (View/UI) e Utilitários ---
COR_VERDE = '\033[92m'
COR_VERMELHA = '\033[91m'
COR_AMARELA = '\033[93m'
COR_AZUL = '\033[94m'
NEGRITO = '\033[1m'
RESET_COR = '\033[0m'

# --- Exceções Customizadas (Melhoria v2.0) ---
class ErroBancario(Exception):
    """Classe base para exceções customizadas do sistema bancário."""
    pass

class SaldoInsuficienteError(ErroBancario):
    """Lançada ao tentar sacar um valor maior que o saldo disponível.

    Attributes:
        saldo (float): O saldo da conta no momento da tentativa.
        valor (float): O valor que se tentou sacar.
        message (str): A mensagem de erro formatada.
    """
    def __init__(self, saldo, valor):
        self.saldo = saldo
        self.valor = valor
        self.message = f"Operação falhou! Saldo insuficiente. (Saldo: R$ {saldo:.2f}, Saque: R$ {valor:.2f})"
        super().__init__(self.message)

class LimiteSaqueError(ErroBancario):
    """Lançada quando um saque excede o limite por operação.

    Attributes:
        limite (float): O limite de saque da conta.
        message (str): A mensagem de erro formatada.
    """
    def __init__(self, limite):
        self.limite = limite
        self.message = f"Operação falhou! O valor do saque excede o limite de R$ {limite:.2f}."
        super().__init__(self.message)

class LimiteQtdSaquesError(ErroBancario):
    """Lançada quando o número de saques diários é excedido."""
    def __init__(self):
        self.message = "Operação falhou! Número máximo de saques diários excedido."
        super().__init__(self.message)

class ValorInvalidoError(ErroBancario):
    """Lançada quando um valor de transação é zero ou negativo."""
    def __init__(self):
        self.message = "Operação falhou! O valor informado deve ser positivo."
        super().__init__(self.message)

# --- Funções de UI e Validação ---
def limpar_tela():
    """Limpa a tela do console."""
    os.system('cls' if os.name == 'nt' else 'clear')

def exibir_mensagem(msg: str, sucesso: bool = True):
    """Exibe uma mensagem de status formatada.

    Args:
        msg (str): A mensagem a ser exibida.
        sucesso (bool, optional): Define a cor da mensagem.
    """
    cor = COR_VERDE if sucesso else COR_VERMELHA
    print(f"\n{cor}{msg}{RESET_COR}")

def pausar_e_limpar():
    """Pausa a execução e limpa a tela."""
    input(f"\n{COR_AMARELA}Pressione Enter para continuar...{RESET_COR}")
    limpar_tela()

def validar_cpf(cpf: str) -> str:
    """Valida o formato do CPF (deve ser numérico e com 11 dígitos).

    Args:
        cpf (str): O CPF a ser validado.

    Returns:
        str: O CPF validado.

    Raises:
        ValueError: Se o CPF for inválido.
    """
    if not cpf.isdigit() or len(cpf) != 11:
        raise ValueError("CPF inválido! Deve conter 11 dígitos numéricos.")
    return cpf

# --- Camada de Modelo (Model) ---
class Transacao(ABC):
    """Classe base abstrata para todas as transações financeiras."""
    @property
    @abstractmethod
    def valor(self) -> float:
        """float: O valor monetário da transação."""
        pass

    @abstractmethod
    def registrar(self, conta: 'Conta'):
        """Registra a transação na conta especificada.

        Args:
            conta (Conta): A instância da conta onde a transação será aplicada.

        Raises:
            ErroBancario: Pode propagar exceções vindas dos métodos da conta.
        """
        pass

class Saque(Transacao):
    """Representa uma transação de saque."""
    def __init__(self, valor: float):
        self._valor = valor

    @property
    def valor(self) -> float:
        return self._valor

    def registrar(self, conta: 'Conta'):
        conta.sacar(self.valor)
        conta.historico.adicionar_transacao(self)

class Deposito(Transacao):
    """Representa uma transação de depósito."""
    def __init__(self, valor: float):
        self._valor = valor

    @property
    def valor(self) -> float:
        return self._valor

    def registrar(self, conta: 'Conta'):
        conta.depositar(self.valor)
        conta.historico.adicionar_transacao(self)

class Historico:
    """Armazena e gerencia o histórico de transações de uma conta."""
    def __init__(self):
        self._transacoes: List[Tuple[datetime, Transacao]] = []

    @property
    def transacoes(self) -> List[Tuple[datetime, Transacao]]:
        """list: Uma cópia da lista de transações para evitar mutações externas."""
        return self._transacoes[:]

    def adicionar_transacao(self, transacao: Transacao):
        """Adiciona uma nova transação ao histórico.

        Args:
            transacao (Transacao): A instância da transação a ser adicionada.
        """
        self._transacoes.append((datetime.now(), transacao))

class Conta:
    """Classe base que representa uma conta bancária de um cliente.

    Attributes:
        _saldo (float): O saldo atual da conta.
        _numero (int): O número único que identifica a conta.
        _agencia (str): O número da agência, fixo em "0001".
        _cliente (Cliente): A instância do cliente proprietário da conta.
        _historico (Historico): O objeto que gerencia o histórico de transações.
    """
    def __init__(self, numero: int, cliente: 'Cliente'):
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
        """Método de fábrica para criar uma nova instância de conta."""
        return cls(numero, cliente)

    def sacar(self, valor: float, /):
        """Realiza um saque na conta, com validações básicas.

        Note:
            A barra (/) na assinatura força `valor` a ser um argumento
            posicional, aumentando a clareza da chamada do método.

        Args:
            valor (float): O valor a ser sacado.

        Raises:
            ValorInvalidoError: Se o valor do saque for menor ou igual a zero.
            SaldoInsuficienteError: Se o valor do saque for maior que o saldo.
        """
        if valor <= 0:
            raise ValorInvalidoError()
        if self._saldo < valor:
            raise SaldoInsuficienteError(self._saldo, valor)
        self._saldo -= valor
        logging.info(f"SAQUE: R$ {valor:.2f} - Conta: {self.numero}")

    def depositar(self, valor: float, /):
        """Realiza um depósito na conta.

        Args:
            valor (float): O valor a ser depositado.

        Raises:
            ValorInvalidoError: Se o valor do depósito for menor ou igual a zero.
        """
        if valor <= 0:
            raise ValorInvalidoError()
        self._saldo += valor
        logging.info(f"DEPÓSITO: R$ {valor:.2f} - Conta: {self.numero}")

class ContaCorrente(Conta):
    """Representa uma conta corrente com regras de negócio específicas."""
    def __init__(self, numero: int, cliente: 'Cliente', limite: float = 500.0, limite_saques: int = 3):
        super().__init__(numero, cliente)
        self._limite = limite
        self._limite_saques = limite_saques

    def sacar(self, valor: float, /):
        """Sobrescreve o método sacar para aplicar regras da conta corrente.

        Args:
            valor (float): O valor a ser sacado.

        Raises:
            LimiteSaqueError: Se o valor exceder o limite por operação.
            LimiteQtdSaquesError: Se o número de saques diários for excedido.
            (Propaga exceções da classe pai: SaldoInsuficienteError, ValorInvalidoError)
        """
        saques_hoje = len([
            t for _, t in self.historico.transacoes if isinstance(t, Saque) and _.date() == datetime.now().date()
        ])
        if valor > self._limite:
            raise LimiteSaqueError(self._limite)
        if saques_hoje >= self._limite_saques:
            raise LimiteQtdSaquesError()

        super().sacar(valor)

class Cliente:
    """Representa um cliente do banco."""
    def __init__(self, nome: str, cpf: str):
        self.nome = nome
        self.cpf = cpf
        self.contas: List[Conta] = []

    def adicionar_conta(self, conta: Conta):
        self.contas.append(conta)

    def realizar_transacao(self, conta: Conta, transacao: Transacao):
        transacao.registrar(conta)

# --- Camada de Controle (Controller) ---
def menu_principal() -> str:
    """Exibe o menu principal e captura a escolha do usuário."""
    menu = """
    ================ MENU ================
    [d]\tDepositar
    [s]\tSacar
    [e]\tExtrato
    [nc]\tNova conta
    [lc]\tListar contas
    [nu]\tNovo usuário
    [q]\tSair
    => """
    return input(textwrap.dedent(menu)).lower().strip()

def filtrar_cliente(cpf: str, clientes: List[Cliente]) -> Optional[Cliente]:
    """Busca um cliente na lista de clientes pelo seu CPF."""
    clientes_filtrados = [c for c in clientes if c.cpf == cpf]
    return clientes_filtrados[0] if clientes_filtrados else None

def recuperar_conta_cliente(cliente: Cliente) -> Optional[Conta]:
    """Recupera a primeira conta associada a um cliente."""
    if not cliente.contas:
        return None
    return cliente.contas[0]

def executar_deposito(clientes: List[Cliente]):
    """Orquestra a operação de depósito, tratando exceções."""
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)
    if not cliente:
        exibir_mensagem("Cliente não encontrado!", sucesso=False)
        return

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        exibir_mensagem("Cliente não possui conta!", sucesso=False)
        return

    try:
        valor = float(input("Informe o valor do depósito: R$ "))
        transacao = Deposito(valor)
        cliente.realizar_transacao(conta, transacao)
        exibir_mensagem("Depósito realizado com sucesso!")
    except ValueError:
        exibir_mensagem("Valor inválido. A operação foi cancelada.", sucesso=False)
    except ErroBancario as e:
        exibir_mensagem(str(e), sucesso=False)

def executar_saque(clientes: List[Cliente]):
    """Orquestra a operação de saque, tratando exceções."""
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)
    if not cliente:
        exibir_mensagem("Cliente não encontrado!", sucesso=False)
        return

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        exibir_mensagem("Cliente não possui conta!", sucesso=False)
        return

    try:
        valor = float(input("Informe o valor do saque: R$ "))
        transacao = Saque(valor)
        cliente.realizar_transacao(conta, transacao)
        exibir_mensagem("Saque realizado com sucesso!")
    except ValueError:
        exibir_mensagem("Valor inválido. A operação foi cancelada.", sucesso=False)
    except ErroBancario as e:
        exibir_mensagem(str(e), sucesso=False)

def exibir_extrato_cliente(clientes: List[Cliente]):
    """Orquestra a exibição do extrato de um cliente."""
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)
    if not cliente:
        exibir_mensagem("Cliente não encontrado!", sucesso=False)
        return

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        exibir_mensagem("Cliente não possui conta!", sucesso=False)
        return

    header = f"""
    ================ EXTRATO ================
    Titular:\t{conta.cliente.nome}
    Agência:\t{conta.agencia}\t\tConta:\t{conta.numero}
    -----------------------------------------"""
    print(textwrap.dedent(header))

    transacoes = conta.historico.transacoes
    if not transacoes:
        print("Não foram realizadas movimentações.")
    else:
        for data, transacao in transacoes:
            tipo = type(transacao).__name__
            cor = COR_VERDE if tipo == 'Deposito' else COR_VERMELHA
            print(f"{data.strftime('%d/%m/%Y %H:%M:%S')} - {tipo:<10s} - {cor}R$ {transacao.valor:10.2f}{RESET_COR}")
    print("-----------------------------------------")
    print(f"Saldo atual:\t{COR_VERDE}R$ {conta.saldo:.2f}{RESET_COR}")
    print("=========================================")

def criar_cliente(clientes: List[Cliente]):
    """Orquestra a criação de um novo cliente com validação de CPF."""
    try:
        cpf = validar_cpf(input("Informe o CPF (11 dígitos, somente números): "))
        if filtrar_cliente(cpf, clientes):
            exibir_mensagem("Já existe um cliente com este CPF!", sucesso=False)
            return

        nome = input("Informe o nome completo: ")
        novo_cliente = Cliente(nome=nome, cpf=cpf)
        clientes.append(novo_cliente)
        exibir_mensagem("Cliente criado com sucesso!")

    except ValueError as e:
        exibir_mensagem(str(e), sucesso=False)

def criar_conta(contas: List[Conta], clientes: List[Cliente]):
    """Orquestra a criação de uma nova conta."""
    cpf = input("Informe o CPF do cliente para vincular a conta: ")
    cliente = filtrar_cliente(cpf, clientes)
    if not cliente:
        exibir_mensagem("Cliente não encontrado!", sucesso=False)
        return

    numero_conta = len(contas) + 1
    conta = ContaCorrente(numero=numero_conta, cliente=cliente)
    cliente.adicionar_conta(conta)
    contas.append(conta)
    exibir_mensagem("Conta corrente criada e vinculada com sucesso!")

def listar_contas(contas: List[Conta]):
    """Exibe uma lista de todas as contas cadastradas."""
    if not contas:
        print("\nNenhuma conta cadastrada.")
        return

    for conta in contas:
        linha = f"""
            -----------------------------------------
            Titular:\t{conta.cliente.nome}
            Agência:\t{conta.agencia}
            C/C:\t\t{conta.numero}
        """
        print(textwrap.dedent(linha))

def main():
    """Função principal que inicializa e executa o loop do sistema bancário."""
    limpar_tela()
    clientes: List[Cliente] = []
    contas: List[Conta] = []

    while True:
        opcao = menu_principal()
        limpar_tela()

        if opcao == 'd':
            executar_deposito(clientes)
        elif opcao == 's':
            executar_saque(clientes)
        elif opcao == 'e':
            exibir_extrato_cliente(clientes)
        elif opcao == 'nu':
            criar_cliente(clientes)
        elif opcao == 'nc':
            criar_conta(contas, clientes)
        elif opcao == 'lc':
            listar_contas(contas)
        elif opcao == 'q':
            print("Encerrando o sistema... Obrigado!")
            break
        else:
            exibir_mensagem("Opção inválida!", sucesso=False)

        if opcao != 'q':
            pausar_e_limpar()

if __name__ == "__main__":
    main()
