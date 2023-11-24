from neo4j import GraphDatabase

class PlataformaConexoes:

    def __init__(self, endereco, user, password):
        self.conexao = GraphDatabase.driver(endereco, auth=(user, password))

    def encerrar(self):
        self.conexao.close()

    def inserir_usuario(self, nome_usuario, faixa_etaria, endereco):
        with self.conexao.session() as sessao:
            return sessao.write_transaction(self._criar_usuario, nome_usuario, faixa_etaria, endereco)

    @staticmethod
    def _criar_usuario(tx, nome_usuario, faixa_etaria, endereco):
        comando = (
            "CREATE (u:Usuario {nome: $nome_usuario, idade: $faixa_etaria, endereco: $endereco}) "
            "RETURN id(u) AS identificador"
        )
        return tx.run(comando, nome_usuario=nome_usuario, faixa_etaria=faixa_etaria, endereco=endereco).single()["identificador"]

    def estabelecer_conexao(self, id_usuario1, id_usuario2):
        with self.conexao.session() as sessao:
            sessao.write_transaction(self._formar_conexao, id_usuario1, id_usuario2)

    @staticmethod
    def _formar_conexao(tx, id_usuario1, id_usuario2):
        comando = (
            "MATCH (a:Usuario), (b:Usuario) "
            "WHERE id(a) = $id_usuario1 AND id(b) = $id_usuario2 "
            "CREATE (a)-[:CONECTADO_COM]->(b) "
            "RETURN a, b"
        )
        tx.run(comando, id_usuario1=id_usuario1, id_usuario2=id_usuario2)

    def exibir_usuarios(self):
        with self.conexao.session() as sessao:
            return sessao.read_transaction(self._listar_usuarios)

    @staticmethod
    def _listar_usuarios(tx):
        comando = "MATCH (u:Usuario) RETURN id(u) AS identificador, u.nome AS nome"
        return tx.run(comando).data()

    def visualizar_conexoes(self, id_usuario):
        with self.conexao.session() as sessao:
            return sessao.read_transaction(self._visualizar_conexoes, id_usuario)

    @staticmethod
    def _visualizar_conexoes(tx, id_usuario):
        comando = (
            "MATCH (u:Usuario)-[:CONECTADO_COM]->(conexao) "
            "WHERE id(u) = $id_usuario "
            "RETURN id(conexao) AS identificador, conexao.nome AS nome"
        )
        return tx.run(comando, id_usuario=id_usuario).data()

    def excluir_usuario(self, id_usuario):
        with self.conexao.session() as sessao:
            sessao.write_transaction(self._excluir_usuario, id_usuario)

    @staticmethod
    def _excluir_usuario(tx, id_usuario):
        comando = (
            "MATCH (u:Usuario) "
            "WHERE id(u) = $id_usuario "
            "DETACH DELETE u"
        )
        tx.run(comando, id_usuario=id_usuario)

def menu_principal():
    print("\nMenu Principal - Plataforma de Conexões:")
    print("1. Inserir Usuário")
    print("2. Estabelecer Conexão")
    print("3. Exibir Usuários")
    print("4. Visualizar Conexões")
    print("5. Excluir Usuário")
    print("6. Encerrar Programa")
    opcao = input("Selecione uma opção: ")
    return opcao

def main():
    endereco = "neo4j://localhost:7687"
    user = "neo4j"
    password = "921737383"

    plataforma = PlataformaConexoes(endereco, user, password)

    while True:
        opcao = menu_principal()

        if opcao == '1':
            nome_usuario = input("Nome do usuário: ")
            faixa_etaria = input("Idade do usuário: ")
            endereco = input("Endereço do usuário: ")
            id_usuario = plataforma.inserir_usuario(nome_usuario, int(faixa_etaria), endereco)
            print(f"Usuário adicionado com ID: {id_usuario}")

        elif opcao == '2':
            id_usuario1 = int(input("ID do primeiro usuário: "))
            id_usuario2 = int(input("ID do segundo usuário: "))
            plataforma.estabelecer_conexao(id_usuario1, id_usuario2)
            print("Conexão estabelecida.")

        elif opcao == '3':
            usuarios = plataforma.exibir_usuarios()
            for usuario in usuarios:
                print(f"ID: {usuario['identificador']}, Nome: {usuario['nome']}")

        elif opcao == '4':
            id_usuario = int(input("ID do usuário: "))
            conexoes = plataforma.visualizar_conexoes(id_usuario)
            for conexao in conexoes:
                print(f"ID: {conexao['identificador']}, Nome: {conexao['nome']}")

        elif opcao == '5':
            id_usuario = int(input("ID do usuário a ser excluído: "))
            plataforma.excluir_usuario(id_usuario)
            print("Usuário excluído.")

        elif opcao == '6':
            break

        else:
            print("Opção inválida.")

    plataforma.encerrar()

if __name__ == "__main__":
    main()
