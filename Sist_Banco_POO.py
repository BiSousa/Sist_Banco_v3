import textwrap
from abc import ABC, abstractclassmethod, abstractproperty
from datetime import datetime

class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def realiza_transacao(self, conta, transacao):
        transacao.registrar(conta)
    
    def adiciona_conta(self, conta):
        self.contas.append(conta)

class PessoaFisica(Cliente):
    def __init__(self, nome, data_nasc, cpf, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.data_nasc = data_nasc
        self.cpf = cpf

class Conta:
    def __init__(self, num, cliente):
        self._saldo = 0
        self._num = num
        self._agencia = '0001'
        self._cliente = cliente
        self._historico = Historico()

    @classmethod
    def nova_conta(cls, cliente, num):
        return cls(num, cliente)
    
    @property
    def saldo(self):
        return self._saldo

    @property
    def num(self):
        return self._num

    @property
    def agencia(self):
        return self._agencia
    
    @property
    def cliente(self):
        return self._cliente
    
    @property
    def historico(self):
        return self._historico

    def sacar(self, valor):
        saldo = self.saldo
        
        if valor > saldo:
            print("Operação inválida. Saldo insuficiente.")
        elif valor > 0:
            self._saldo -= valor
            print("Saque realizado!")
            return True
        else:
            print("Operação inválida. O valor não é válido.")
        return False
    
    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            print("Depósito realizado!")
        else:
            print("Não é possível realizar o depósito!")
        
        return True

class ContaCorrente(Conta):
    def __init__(self, num, cliente, limite = 500, limite_saques = 3):
        super().__init__(num, cliente)
        self.limite = limite
        self.limite_saque = limite_saques

    def sacar(self, valor):
        num_saques = len([transacao for transacao in self.historico.transacoes if transacao["tipo"] == Saque.__name__])

        if valor > self.limite:
            print("Falha na operação. O valor é maior que o limite.")
        elif num_saques >= self.limite_saques:
            print("Limite de saques diários atingido.")
        else:
            return super().sacar(valor)
        return False
    
    def __str__(self):
        return f"""\
            Agência:\t{self.agencia}
            C/C:\t\t{self.num}
            Titular:\t{self.cliente.nome}
        """

class Historico:
    def __init__(self):
        self._transacoes = []
    
    @property
    def transacoes(self):
        return self._transacoes
    
    def adiciona_transacao(self, transacao):
        self._transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "valor": transacao.valor,
                "data": datetime.now().strftime("%d-%m-%Y %H:%M:%s"),
            }
        )

class Transacao (ABC):
    @property
    @abstractproperty
    def valor(self):
        pass

    @abstractclassmethod
    def registra(self, conta):
        pass

class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor
    
    @property
    def valor(self):
        return self._valor
    
    def registra(self, conta):
        transacao_sucesso = conta.sacar(self.valor)

        if transacao_sucesso:
            conta.historico.adiciona_transacao(self)

class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor
    
    @property
    def valor(self):
        return self._valor
    
    def registra(self, conta):
        transacao_sucesso = conta.depositar(self.valor)

        if transacao_sucesso:
            conta.historico.adiciona_transacao(self)


def menu():
    menu = """

    [0] - Depositar
    [1] - Sacar
    [2] - Extrato
    [3] - Novo usuário
    [4] - Nova conta
    [5] - Listar contas
    [6] - Sair

    --> """
    return input(menu)

def depositar(clientes):
    cpf = input("Caro(a) cliente, informe o CPF: ")
    cliente = filtra_usuario(cpf, clientes)

    if not cliente:
        print("Cliente não encontrado!")
        return
    
    valor = float(input("Informe o valor a ser depositado: "))
    transacao = Deposito(valor)

    conta = recupera_conta(cliente)
    if not conta:
        return
    
    cliente.realiza_transacao(conta, transacao)

def sacar(clientes):
    cpf = input("Caro(a) clientes, informe o CPF: ")
    cliente = filtra_usuario(cpf, clientes)

    if not cliente:
        print("Cliente não encontrado!")
        return
    
    valor = float(input("Informe o valor do saque: "))
    transacao = Saque(valor)

    conta = recupera_conta(cliente)
    if not conta:
        return
    
    cliente.realiza_transacao(conta, transacao)

def recupera_conta(cliente):
    if not cliente.contas:
        print("Cliente não possui conta!")
        return
    
    return cliente.contas[0]

def mostrar_extrato(clientes):
    cpf = input("Caro(a) cliente, informe o CPF: ")
    cliente = filtra_usuario(cpf, clientes)

    if not cliente:
        print("Cliente não encontrado!")

    conta = recupera_conta(cliente)
    if not conta:
        return

    print("\n----------EXTRATO----------")
    transacoes = conta.historico.transacoes

    extrato = ""
    if not transacoes:
        extrato = "Não foram realizadas movimentações."
    else:
        for transacao in transacoes:
            extrato += f"\n{transacao['tipo']}:\n\tR${transacao['valor']:.2f}"

    print(extrato)
    print(f"\nSaldo: \n\tR$ {conta.saldo:.2f}")
    print("---------------------------")

def cria_usuario(clientes):
    cpf = input("Informe o CPF: ")
    cliente = filtra_usuario(cpf, clientes)

    if cliente:
        print("O usuário já existe!")
        return
    
    nome = input("Nome completo: ")
    data_nasc = input("Data de nascimento (dd-mm-aaaa): ")
    endereco = input("Informe o endereço (logradouro, nro - bairro - cidade/sigla estado): ")

    cliente = PessoaFisica(nome = nome, data_nasc = data_nasc, cpf = cpf, endereco = endereco)

    clientes.append(cliente)

    print("Usuário criado!")
    
def filtra_usuario(cpf, clientes):
    clientes_filtrados = [cliente for cliente in clientes if cliente["cpf"] == cpf]
    return clientes_filtrados[0] if clientes_filtrados else None

def cria_conta(numero_conta, clientes, contas):
    cpf = input("Caro(a) cliente, insira o CPF: ")
    cliente = filtra_usuario(cpf, clientes)

    if not cliente:
        print("Cliente não encontrado!")
        return
    
    conta = ContaCorrente.nova_conta(cliente = cliente, numero = numero_conta)
    contas.append(conta)
    cliente.contas.append(conta)

    print("Contra criada!")

def lista_contas(contas):
    for conta in contas:
        print("=" * 100)
        print(textwrap.dedent(str(conta)))

def main():
    menu()

    contas = []
    clientes = []

    while True:
        opcao = menu()

        if opcao ==  "0": #DEPÓSITO
            depositar(clientes)           
        elif opcao == "1": #SAQUE
            sacar(clientes)
        elif opcao == "2": #EXIBIR EXTRATO
            mostrar_extrato(clientes)
        elif opcao == "3": #NOVO USUÁRIO
            cria_usuario(clientes)
        elif opcao == "4": #NOVA CONTA
            numero_conta = len(contas) + 1
            conta = cria_conta(numero_conta, clientes, contas)
        elif opcao == "5": #LISTAR CONTAS
            lista_contas(contas)
        elif opcao == "6": #SAIR
            print("Até a próxima operação!")
            break
        else:
            print("Operação inválida. Insira uma operação válida!")

main()