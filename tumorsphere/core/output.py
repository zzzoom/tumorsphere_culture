from abc import ABC, abstractmethod

import sqlite3
import logging
import os


class TumorsphereOutput(ABC):
    @abstractmethod
    def begin_culture(
        self,
        prob_stem,
        prob_diff,
        rng_seed,
        simulation_start,
        adjacency_threshold,
        swap_probability,
    ):
        pass

    @abstractmethod
    def record_stemness(self, cell_index, tic, stemness):
        pass

    @abstractmethod
    def record_deactivation(self, cell_index, tic):
        pass

    @abstractmethod
    def record_num_cells(
        self, num_cells, num_active, num_stem, num_active_stem
    ):
        pass

    # FIXME: These two are redundant
    @abstractmethod
    def dump_cell_positions(self, t, cells, cell_positions):
        pass

    @abstractmethod
    def record_cell(
        self, index, parent, pos_x, pos_y, pos_z, creation_time, is_stem
    ):
        pass


class OutputDemux(TumorsphereOutput):
    def __init__(self, culture_name, result_list):
        self.culture_name = culture_name
        self.result_list = result_list

    def begin_culture(
        self,
        prob_stem,
        prob_diff,
        rng_seed,
        simulation_start,
        adjacency_threshold,
        swap_probability,
    ):
        for result in self.result_list:
            result.begin_culture(
                prob_stem,
                prob_diff,
                rng_seed,
                simulation_start,
                adjacency_threshold,
                swap_probability,
            )

    def record_stemness(self, cell_index, tic, stemness):
        for result in self.result_list:
            result.record_stemness(cell_index, tic, stemness)

    def record_deactivation(self, cell_index, tic):
        for result in self.result_list:
            result.record_deactivation(cell_index, tic)

    def record_num_cells(
        self, num_cells, num_active, num_stem, num_active_stem
    ):
        for result in self.result_list:
            result.record_num_cells(
                num_cells, num_active, num_stem, num_active_stem
            )

    def dump_cell_positions(self, t, cells, cell_positions):
        for result in self.result_list:
            result.dump_cell_positions(t, cells, cell_positions)

    def record_cell(
        self, index, parent, pos_x, pos_y, pos_z, creation_time, is_stem
    ):
        for result in self.result_list:
            result.record_cell(
                index, parent, pos_x, pos_y, pos_z, creation_time, is_stem
            )


class SQLOutput(TumorsphereOutput):
    def __init__(self, culture_name):
        # connection to the SQLite database
        # we connect into a 'data' directory, if not present, we warn
        # and connect to a db in the current folder
        self.conn = None
        try:
            self.conn = sqlite3.connect(f"data/{culture_name}.db")
        except sqlite3.OperationalError:
            print(
                "The 'data' directory does not exist. The database will be "
                "created in the current folder."
            )
            self.conn = sqlite3.connect(f"{culture_name}.db")

        cursor = self.conn.cursor()

        # Enable foreign key constraints for this connection
        cursor.execute("PRAGMA foreign_keys = ON;")

        # Creating the Culture table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Cultures (
                culture_id INTEGER PRIMARY KEY AUTOINCREMENT,
                prob_stem REAL NOT NULL,
                prob_diff REAL NOT NULL,
                culture_seed INTEGER NOT NULL,
                simulation_start TIMESTAMP NOT NULL,
                adjacency_threshold REAL NOT NULL,
                swap_probability REAL NOT NULL
            );
            """
        )
        # Creating the Cells table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Cells (
            _index INTEGER PRIMARY KEY,
            parent_index INTEGER,
            position_x REAL NOT NULL,
            position_y REAL NOT NULL,
            position_z REAL NOT NULL,
            t_creation INTEGER NOT NULL,
            t_deactivation INTEGER,
            culture_id INTEGER,
            FOREIGN KEY(culture_id) REFERENCES Cultures(culture_id)
            );
            """
        )
        # Creating the StemChange table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS StemChanges (
            change_id INTEGER PRIMARY KEY AUTOINCREMENT,
            cell_id INTEGER NOT NULL,
            t_change INTEGER NOT NULL,
            is_stem BOOLEAN NOT NULL,
            FOREIGN KEY(cell_id) REFERENCES Cells(_index)
            );
            """
        )

    def begin_culture(
        self,
        prob_stem,
        prob_diff,
        rng_seed,
        simulation_start,
        adjacency_threshold,
        swap_probability,
    ) -> int:
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                INSERT INTO Cultures (prob_stem, prob_diff, culture_seed, simulation_start, adjacency_threshold, swap_probability)
                VALUES (?, ?, ?, ?, ?, ?);
            """,
                (
                    prob_stem,
                    prob_diff,
                    int(rng_seed),
                    simulation_start,
                    adjacency_threshold,
                    swap_probability,
                ),
            )
            self.culture_id = cursor.lastrowid

    def record_stemness(self, cell_index, tic, stemness):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                INSERT INTO StemChanges (cell_id, t_change, is_stem)
                VALUES (?, ?, ?);
            """,
                (
                    int(cell_index),
                    tic,
                    stemness,
                ),
            )

    def record_deactivation(self, cell_index, tic):
        with self.conn:
            cursor = self.conn.cursor()

            # Recording (updating) the t_deactivation value for the specified cell
            cursor.execute(
                """
                UPDATE Cells
                SET t_deactivation = ?
                WHERE _index = ?;
                """,
                (tic, int(cell_index)),
            )

    def record_num_cells(
        self, num_cells, num_active, num_stem, num_active_stem
    ):
        pass

    def dump_cell_positions(self, t, cells, cell_positions):
        pass

    def record_cell(
        self, index, parent, pos_x, pos_y, pos_z, creation_time, is_stem
    ):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                INSERT INTO Cells (_index, parent_index, position_x, position_y, position_z, t_creation, culture_id)
                VALUES (?, ?, ?, ?, ?, ?, ?);
            """,
                (
                    index,
                    parent,
                    pos_x,
                    pos_y,
                    pos_z,
                    creation_time,
                    self.culture_id,
                ),
            )
            cursor.execute(
                """
                INSERT INTO StemChanges (cell_id, t_change, is_stem)
                VALUES (?, ?, ?);
            """,
                (
                    index,
                    creation_time,
                    is_stem,
                ),
            )


class DatOutput(TumorsphereOutput):
    def __init__(self, culture_name):
        self.filename = f"data/{culture_name}.dat"
        with open(self.filename, "w") as datfile:
            datfile.write("total, active, total_stem, active_stem \n")

    def begin_culture(
        self,
        prob_stem,
        prob_diff,
        rng_seed,
        simulation_start,
        adjacency_threshold,
        swap_probability,
    ):
        pass

    def record_stemness(self, cell_index, tic, stemness):
        pass

    def record_deactivation(self, cell_index, tic):
        pass

    def record_num_cells(
        self, num_cells, num_active, num_stem, num_active_stem
    ):
        with open(self.filename, "a") as datfile:
            datfile.write(
                f"{num_cells}, {num_active}, {num_stem}, {num_active_stem} \n"
            )

    def dump_cell_positions(self, t, cells, cell_positions):
        pass

    def record_cell(
        self, index, parent, pos_x, pos_y, pos_z, creation_time, is_stem
    ):
        pass


class OvitoOutput(TumorsphereOutput):
    def __init__(self, culture_name):
        self.culture_name = culture_name

    def begin_culture(
        self,
        prob_stem,
        prob_diff,
        rng_seed,
        simulation_start,
        adjacency_threshold,
        swap_probability,
    ):
        pass

    def record_stemness(self, cell_index, tic, stemness):
        pass

    def record_deactivation(self, cell_index, tic):
        pass

    def record_num_cells(
        self, num_cells, num_active, num_stem, num_active_stem
    ):
        pass

    def dump_cell_positions(self, t, cells, cell_positions):
        """Writes the data file in path for ovito, for time step t of self.
        Auxiliar function for simulate_with_ovito_data.
        """
        path_to_write = f"data/ovito_data_{self.culture_name}.{t:03}"
        with open(path_to_write, "w") as file_to_write:
            file_to_write.write(str(len(cells)) + "\n")
            file_to_write.write(
                ' Lattice="1.0 0.0 0.0 0.0 1.0 0.0 0.0 0.0 1.0"Properties=species:S:1:pos:R:3:Color:r:1'
                + "\n"
            )

            for cell in cells:  # csc activas
                if cell.is_stem and cell.available_space:
                    line = (
                        "active_stem "
                        + str(cell_positions[cell._index][0])
                        + " "
                        + str(cell_positions[cell._index][1])
                        + " "
                        + str(cell_positions[cell._index][2])
                        + " "
                        + "1"
                        + "\n"
                    )
                    file_to_write.write(line)

            for cell in cells:  # csc quiesc
                if cell.is_stem and (not cell.available_space):
                    line = (
                        "quiesc_stem "
                        + str(cell_positions[cell._index][0])
                        + " "
                        + str(cell_positions[cell._index][1])
                        + " "
                        + str(cell_positions[cell._index][2])
                        + " "
                        + "2"
                        + "\n"
                    )
                    file_to_write.write(line)

            for cell in cells:  # dcc activas
                if (not cell.is_stem) and cell.available_space:
                    line = (
                        "active_diff "
                        + str(cell_positions[cell._index][0])
                        + " "
                        + str(cell_positions[cell._index][1])
                        + " "
                        + str(cell_positions[cell._index][2])
                        + " "
                        + "3"
                        + "\n"
                    )
                    file_to_write.write(line)

            for cell in cells:  # dcc quiesc
                if not (cell.is_stem or cell.available_space):
                    line = (
                        "quiesc_diff "
                        + str(cell_positions[cell._index][0])
                        + " "
                        + str(cell_positions[cell._index][1])
                        + " "
                        + str(cell_positions[cell._index][2])
                        + " "
                        + "4"
                        + "\n"
                    )
                    file_to_write.write(line)

    def record_cell(
        self, index, parent, pos_x, pos_y, pos_z, creation_time, is_stem
    ):
        pass


def create_output_demux(
    culture_name: str,
    requested_outputs: list[str],
):
    output_types = {
        "sql": SQLOutput,
        "dat": DatOutput,
        "ovito": OvitoOutput,
    }
    outputs = []
    for out in requested_outputs:
        if out in output_types:
            outputs.append(output_types[out](culture_name))
        else:
            logging.warning(f"Invalid output {out} requested")
    return OutputDemux(culture_name, outputs)
