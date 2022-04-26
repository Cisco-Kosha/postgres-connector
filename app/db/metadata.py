class TableMetadata(object):
    table: str = None

    def set_table(self, table):
        self.table = table

    def get_table(self):
        if self.table:
            return self.table
        else:
            return None


table_metadata = TableMetadata()
