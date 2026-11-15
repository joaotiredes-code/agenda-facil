"""Exceções da camada de modelo."""


class ValidationError(Exception):
    """Erro de validação ou de regra de negócio.

    Carrega uma lista de mensagens amigáveis para exibir ao usuário.
    """

    def __init__(self, mensagens):
        if isinstance(mensagens, str):
            mensagens = [mensagens]
        self.mensagens = list(mensagens)
        super().__init__("; ".join(self.mensagens))
