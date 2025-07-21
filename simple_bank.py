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
            if isinstance(transacao, Saque) and _.date() == datetime.now().date()
        ])

        if valor > self._limite:
            msg_erro = f"Falha! Valor (R$ {valor:.2f}) excede o limite de R$ {self._limite:.2f}."
            logging.warning(msg_erro)
            print(f"{COR_VERMELHA}{msg_erro}{RESET_COR}")
            return False

        if saques_hoje >= self._limite_saques:
            msg_erro = "Falha! Número máximo de saques diários excedido."
            logging.warning(msg_erro)
            print(f"{COR_VERMELHA}{msg_erro}{RESET_COR}")
            return False

        return super().sacar(valor)


class Cliente:
    """Representa um cliente do banco.

    Um cliente possui dados pessoais e uma lista de contas bancárias.

    Attributes:
        nome (str): Nome completo do cliente.
        cpf (str): CPF do cliente (usado como identificador).
        contas (list): Lista de instâncias de Conta associadas ao cliente.
    """

    def __init__(self, nome: str, cpf: str):
        """Inicializa uma instância de Cliente.

        Args:
            nome (str): O nome do cliente.
            cpf (str): O CPF do cliente.
        """
        self.nome: str = nome
        self.cpf: str = cpf
        self.contas: List[Conta] = []

    def adicionar_conta(self, conta: Conta):
        """Associa uma conta a este cliente.

        Args:
            conta (Conta): A instância da conta a ser adicionada.
        """
        self.contas.append(conta)

    def realizar_transacao(self, conta: Conta, transacao: Transacao):
        """Inicia uma transação em uma das contas do cliente.

        Args:
            conta (Conta): A conta onde a transação deve ocorrer.
            transacao (Transacao): A transação a ser executada (Saque ou Depósito).
        """
        transacao.registrar(conta)


# --- Camada de Controle (Controller) ---

def menu_principal() -> str:
    """Exibe o menu principal de operações e captura a escolha do usuário.

    Returns:
        str: A opção selecionada pelo usuário, convertida para minúsculas.
    """
    print("\n" + "="*40)
    print(f"|{COR_AZUL+NEGRITO}      BANCO DIGITAL - PRO v1.0      {RESET_COR}|")
    print("="*40)
    print("  [d] Depositar\n  [s] Sacar\n  [e] Extrato\n  [u] Novo Usuário")
    print("  [c] Nova Conta\n  [l] Listar Contas\n  [q] Sair")
    return input(f"\n{NEGRITO}=> {RESET_COR}").lower().strip()


def filtrar_cliente(cpf: str, clientes: List[Cliente]) -> Optional[Cliente]:
    """Busca um cliente na lista de clientes pelo seu CPF.

    Args:
        cpf (str): O CPF a ser pesquisado.
        clientes (list): A lista de todos os clientes cadastrados.

    Returns:
        Optional[Cliente]: A instância do cliente encontrado ou None se não existir.
    """
    clientes_filtrados = [c for c in clientes if c.cpf == cpf]
    return clientes_filtrados[0] if clientes_filtrados else None


def recuperar_conta_cliente(cliente: Cliente) -> Optional[Conta]:
    """Recupera a primeira conta associada a um cliente.

    Note:
        Esta é uma simplificação. Em um sistema real, o usuário poderia
        escolher entre múltiplas contas.

    Args:
        cliente (Cliente): O cliente do qual a conta será recuperada.

    Returns:
        Optional[Conta]: A primeira conta da lista do cliente ou None se ele
            não possuir contas.
    """
    if not cliente.contas:
        print(f"\n{COR_VERMELHA}Cliente não possui conta!{RESET_COR}")
        return None
    return cliente.contas[0]


def executar_deposito(clientes: List[Cliente]):
    """Orquestra a operação de depósito para um cliente.

    Args:
        clientes (list): A lista de clientes do sistema.
    """
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        exibir_mensagem("Cliente não encontrado!", sucesso=False)
        return

    try:
        valor = float(input("Informe o valor do depósito: R$ "))
        conta = recuperar_conta_cliente(cliente)
        if conta:
            transacao = Deposito(valor)
            cliente.realizar_transacao(conta, transacao)
            exibir_mensagem("Depósito realizado com sucesso!")
    except ValueError:
        exibir_mensagem("Valor inválido. A operação foi cancelada.", sucesso=False)


def executar_saque(clientes: List[Cliente]):
    """Orquestra a operação de saque para um cliente.

    Args:
        clientes (list): A lista de clientes do sistema.
    """
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        exibir_mensagem("Cliente não encontrado!", sucesso=False)
        return

    try:
        valor = float(input("Informe o valor do saque: R$ "))
        conta = recuperar_conta_cliente(cliente)
        if conta:
            transacao = Saque(valor)
            cliente.realizar_transacao(conta, transacao)
    except ValueError:
        exibir_mensagem("Valor inválido. A operação foi cancelada.", sucesso=False)


def exibir_extrato_cliente(clientes: List[Cliente]):
    """Orquestra a exibição do extrato de um cliente.

    Args:
        clientes (list): A lista de clientes do sistema.
    """
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)
    if not cliente:
        exibir_mensagem("Cliente não encontrado!", sucesso=False)
        return

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    print("\n" + "=" * 40)
    print(f"|{COR_AZUL+NEGRITO}              EXTRATO               {RESET_COR}|")
    print("=" * 40)
    print(f"Titular: {conta.cliente.nome}")
    print(f"Agência: {conta.agencia}\tConta: {conta.numero}")
    print("-" * 40)

    transacoes = conta.historico.transacoes
    if not transacoes:
        print("Não foram realizadas movimentações.")
    else:
        for data, transacao in transacoes:
            tipo = type(transacao).__name__
            cor = COR_VERDE if tipo == 'Deposito' else COR_VERMELHA
            print(f"{data.strftime('%d/%m/%Y %H:%M:%S')} - {tipo:<10s} - "
                  f"{cor}R$ {transacao.valor:10.2f}{RESET_COR}")

    print("-" * 40)
    print(f"Saldo atual: {COR_VERDE}R$ {conta.saldo:.2f}{RESET_COR}")
    print("=" * 40)


def criar_cliente(clientes: List[Cliente]):
    """Orquestra a criação de um novo cliente.

    Args:
        clientes (list): A lista de clientes, que será modificada se o
            novo cliente for criado.
    """
    cpf = input("Informe o CPF (somente números): ")
    if filtrar_cliente(cpf, clientes):
        exibir_mensagem("Já existe um cliente com este CPF!", sucesso=False)
        return

    nome = input("Informe o nome completo: ")
    novo_cliente = Cliente(nome=nome, cpf=cpf)
    clientes.append(novo_cliente)
    exibir_mensagem("Cliente criado com sucesso!")
    logging.info(f"Novo cliente criado: {nome} (CPF: {cpf})")


def criar_conta(numero_conta: int, clientes: List[Cliente]) -> Optional[Conta]:
    """Orquestra a criação de uma nova conta para um cliente.

    Args:
        numero_conta (int): O número a ser atribuído para a nova conta.
        clientes (list): A lista de clientes para encontrar o titular da conta.

    Returns:
        Optional[Conta]: A instância da conta recém-criada ou None se a
            operação falhar.
    """
    cpf = input("Informe o CPF do cliente para vincular a conta: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        exibir_mensagem("Cliente não encontrado!", sucesso=False)
        return None

    conta = ContaCorrente(numero=numero_conta, cliente=cliente)
    cliente.adicionar_conta(conta)
    exibir_mensagem("Conta corrente criada e vinculada com sucesso!")
    logging.info(f"Nova conta {conta.numero} criada para o cliente {cliente.cpf}.")
    return conta


def listar_contas_clientes(clientes: List[Cliente]):
    """Exibe uma lista de todos os clientes e suas respectivas contas.

    Args:
        clientes (list): A lista de todos os clientes cadastrados.
    """
    if not clientes:
        print("\nNenhum cliente cadastrado.")
        return
        
    for cliente in clientes:
        print("\n" + "=" * 40)
        print(f"Titular: {cliente.nome}\nCPF: {cliente.cpf}")
        if not cliente.contas:
            print("  (Sem contas cadastradas)")
        else:
            for conta in cliente.contas:
                print(f"  Agência: {conta.agencia} | Conta: {conta.numero} | Saldo: R$ {conta.saldo:.2f}")


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
        elif opcao == 'u':
            criar_cliente(clientes)
        elif opcao == 'c':
            numero_conta = len(contas) + 1
            nova_conta = criar_conta(numero_conta, clientes)
            if nova_conta:
                contas.append(nova_conta)
        elif opcao == 'l':
            listar_contas_clientes(clientes)
        elif opcao == 'q':
            print("Encerrando o sistema... Obrigado!")
            break
        else:
            exibir_mensagem("Opção inválida!", sucesso=False)
        
        if opcao != 'q':
            pausar_e_limpar()


if __name__ == "__main__":
    main()
