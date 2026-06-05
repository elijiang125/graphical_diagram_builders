import braket.circuits.circuit as cir
from braket.circuits.graphical_diagram_builders.graphical_circuit_diagram import (
    GraphicalCircuitDiagram,
)
from braket.circuits.graphical_diagram_builders.graphical_diagram_utils import (
    BarrierMarker,
    CircuitLayout,
    Connection,
    ControlDot,
    GateBox,
    SwapMarker,
)
from braket.circuits.moments import MomentType

import plotly.graph_objects as go

# 1. Definitions:
#         A MomentType is a strEnum (enumeration of Strings) containing:
#             GATE: a gate -> "gate"
#             NOISE: a noise channel added directly to the circuit -> "noise"
#             GATE_NOISE: a gate-based noise channel -> "gate_noise"
#             INITIALIZATION_NOISE: a initialization noise channel -> "initialization_noise"
#             READOUT_NOISE: a readout noise channel -> "readout_noise"
#             COMPILER_DIRECTIVE: an instruction to the compiler, external to the quantum program itself -> "compiler_directive"
#             MEASURE: a measurement -> "measure"

#         A QubitSetInput is ONE of:
#          Qubit Data Structure
#          Integer
#          Iterable of [Qubit OR Integer]

#         A Qubit Set is a QubitSetInput

#         A MomentsKey is a NamedTuple containing:
#             Integer -> time
#             QubitSet -> qubits
#             MomentType -> moment_type
#             Integer -> noise_index
#             Integer -> subindex

#         An Instruction is a Data Structure containing:
#             Instruction Operator DS-> operator
#             QubitSetInput OR None -> target
#             QubitSetInput OR None -> control
#             BasisStateInput OR None -> control_state
#             Float -> power
            
#         A Moments is a Data Structure containing:
#             OrderedDictionary of [MomentsKey, Instruction]] -> self._moments
#             Dictionary of [Qubit, Integer] -> self._max_times
#             QubitSet Data Structure -> self._qubits
#             Integer -> self._depth
#             Integer -> self._time_all_qubits
#             Integer -> self._number_gphase_in_current_moment

#         A Circuit is a Data Structure containing:
#             Moments() Data Structure ->  self._moments
#             Dictionary of ResultType's -> self._result_types
#             Dictionary of [Integers OR Circuit._ALL_QUBITS, Observable] -> self._qubit_observable_mapping
#             Dictionary of [Integers, Tuple of Integers] -> self._qubit_observable_target_mapping
#             Set -> self._qubit_observable_set
#             Set -> self._parameters
#             Boolean -> self._observables_simultaneously_measurable
#             Boolean -> self._requires_physical_qubits
#             None -> self._measure_targets

class PlotlyCircuitDiagram(GraphicalCircuitDiagram):

    # Layout parameters (same params as MatplotlibCircuitDiagram)
    # Note: will be tweaked if doesn't fit with Plotly's rendering style

    COL_WIDTH = 1.4  # default/minimum column width, used as a lower bound
    COL_GAP = 0.2  # horizontal gap between adjacent column boxes
    ROW_HEIGHT = 0.8
    WIRE_EXTEND = 0.5  # extra wire length before first / after last column

    # Gate box style
    GATE_BOX_HEIGHT = 0.5
    GATE_BOX_MIN_WIDTH = 0.6
    GATE_BOX_PADDING = 0.3  # horizontal padding inside the box around the label
    GATE_FONT_SIZE = 10
    GATE_FILL_COLOR = "#D4E6F1"
    GATE_EDGE_COLOR = "black"
    GATE_TEXT_COLOR = "black"

    # Wire style
    WIRE_COLOR = "#333333"
    WIRE_LW = 1.0

    # Control dot style
    CONTROL_DOT_RADIUS = 0.08
    CONTROL_DOT_COLOR = "black"

    # Connection / barrier style
    CONNECTION_LW = 1.5
    CONNECTION_COLOR = "black"
    BARRIER_COLOR = "#888888"
    BARRIER_FILL_COLOR = "#DDDDDD"
    BARRIER_LW = 1.0
    BARRIER_WIDTH = 0.25  # horizontal width of the per-qubit barrier marker
    BARRIER_HEIGHT_FRAC = 0.6  # fraction of ROW_HEIGHT covered by the marker
    BARRIER_HATCH = "///"

    # Label style
    QUBIT_LABEL_FONT_SIZE = 11
    MOMENT_LABEL_FONT_SIZE = 9
    FOOTER_FONT_SIZE = 9

    # Marker sizes
    SWAP_MARKER_SIZE = 8

    @staticmethod
    def build_diagram(circuit: cir.Circuit) -> go.Figure:
        """
        1. Definitions
        Note: Check definition of Circuit above

        An Axis is a Data Structure consisting of:
            String -> title
            Boolean -> show grid or no?

        A Margin is a Data Structure consisting of:
            Number -> top margins in pixels
            Number -> bottom margins in pixels
            Number -> left margins in pixels
            Number -> right margins in pixels

        A Trace is a Data Structure consisting of:
            ListofNumbers -> x coords
            ListofNumbers -> y coords
            String -> mode

        A Layout is a Data Structure consisting of:
            String -> title
            Axis -> x-axis
            Axis -> y-axis
            Margin -> margin

        A PlotlyFigure is a Data Structure consisting of:
            Listof Traces
            Layout

        2. Signature, header, purpose:
            build_diagram: Circuit -> PlotlyFigure
            We are initializing a PlotlyFigure for a circuit. IF:
                1) No instructions for the circuit are provided -> empty plot because it's an empty circuit
                2) All moments in the Circuit's OrderedDictionary's MomentKey's MomentType had the same string as "global_phase" -> bigger plot with Global phase

        """
        if not circuit.instructions:
            fig = go.Figure()
            fig.update_layout(
                autosize=False,
                width = 192, # 1 inch = 96 pixels according to https://pixelsconverter.com/inches-to-pixels, adjust if it doesn't work
                height = 96
            )
            fig.add_annotation(
                x = 0.5,
                y = 0.5,
                xref="paper",
                yref="paper",
                text="(empty circuit)",
                showarrow=False,
                font=dict(size=12)
            )
            fig.update_xaxes(visible=False)
            fig.update_yaxes(visible=False)
            #fig, ax = plt.subplots(figsize=(2, 1))
            #ax.text(0.5, 0.5, "(empty circuit)", ha="center", va="center", fontsize=12)
            #ax.axis("off")
            return fig

        if all(m.moment_type == MomentType.GLOBAL_PHASE for m in circuit._moments):
            fig = go.Figure()
            fig.update_layout(
                autosize=False,
                width = 288, 
                height = 96
            )
            fig.add_annotation(
                x = 0.5,
                y = 0.5,
                xref = "paper",
                yref = "paper",
                text = f"Global phase: {circuit.global_phase}",
                showarrow=False,
                font=dict(size=12)
            )
            fig.update_xaxes(visible=False)
            fig.update_yaxes(visible=False)
            # fig, ax = plt.subplots(figsize=(3, 1))
            # ax.text(
            #     0.5,
            #     0.5,
            #     f"Global phase: {circuit.global_phase}",
            #     ha="center",
            #     va="center",
            #     fontsize=12,
            # )
            # ax.axis("off")
            return fig

        layout = PlotlyCircuitDiagram._compute_layout(circuit)
        return PlotlyCircuitDiagram._render_layout(layout)

    @classmethod 
    def _gate_box_width(cls, label: str) -> float:
        """Return the width of a gate box rendered with *label*."""
        char_width = cls.GATE_FONT_SIZE * 0.012
        text_width = len(label) * char_width
        return max(cls.GATE_BOX_MIN_WIDTH, text_width + cls.GATE_BOX_PADDING)

    @classmethod
    def _compute_column_x(cls, layout: CircuitLayout) -> tuple[list[float], list[float]]:
        """Compute the x center and width of each column based on box sizes.

        Columns are sized to fit the widest gate box they contain, plus a
        fixed gap. Columns with no boxes fall back to the default width.

        Returns:
            Tuple of ``(centers, widths)`` lists of length ``num_moments``.
        """
        n_cols = max(layout.num_moments, 1)
        widths = [cls.COL_WIDTH] * n_cols
        for elem in layout.elements:
            if isinstance(elem, GateBox):
                widths[elem.col] = max(
                    widths[elem.col], cls._gate_box_width(elem.label) + cls.COL_GAP
                )
        centers: list[float] = []
        cursor = 0.0
        for w in widths:
            centers.append((cursor + w / 2))
            cursor += w
        return centers, widths

    @classmethod 
    def _render_layout(cls, layout: CircuitLayout) -> go.Figure:
        """
        1. Definitions
        An Axis is a Data Structure consisting of:
            String -> title
            Boolean -> show grid or no?
        
            A Margin is a Data Structure consisting of:
            Number -> top margins in pixels
            Number -> bottom margins in pixels
            Number -> left margins in pixels
            Number -> right margins in pixels

        A Trace is a Data Structure consisting of:
            ListofNumbers -> x coords
            ListofNumbers -> y coords
            String -> mode

        A Layout is a Data Structure consisting of:
            String -> title
            Axis -> x-axis
            Axis -> y-axis
            Margin -> margin

        A PlotlyFigure is a Data Structure consisting of:
            Listof Traces
            Layout

        A CircuitLayout is a Data Structure consisting of:
            Integer -> num_qubits
            Integer -> num_moments
            Listof strings -> qubit_labels
            Listof Strings -> moment_labels
            Listof ??? -> elements
            Float OR None -> global_phase
            ListofStrings -> additional_result_types
            ListofStrings -> unassigned_parameters

        _render_layout: PlotlyCircuitDiagram + CircuitLayout -> PlotlyFigure

        Given the parameters in PlotlyCircuitDiagram to design the figure along with the CircuitLayout to identify the circuit itself, build a PlotlyFigure of the Circuit

        Matplotlib's axes are needed to pass through helper methods, but Plotly's Axis is just a string and boolean.
        We'll have to require the helper functions that take in a Matplotlib ax, to take in a PlotlyFigure instead.
        """
        n_rows = max(layout.num_qubits, 1)

        col_x, col_w = cls._compute_column_x(layout)
        total_width = sum(col_w)
        right_edge = total_width

        fig_width = max(4, cls.WIRE_EXTEND * 2 + total_width + 1.5)
        fig_height = max(2, n_rows * cls.ROW_HEIGHT + 1.5)

        # Plotly figure initialize
        fig = go.Figure()
        fig.update_yaxes(
            visible=False,
        )
        fig.update_xaxes(visible=False)
        fig.update_layout(
            autosize=False,
            width = fig_width * 96, 
            height = fig_height * 96,
            plot_bgcolor="white",
            paper_bgcolor="white"
        )
        # fig, ax = plt.subplots(figsize=(fig_width, fig_height))

        left_wire = col_x[0] - col_w[0] / 2 - cls.WIRE_EXTEND
        right_wire = right_edge + cls.WIRE_EXTEND

        cls._draw_qubit_wires(fig, layout, left_wire, right_wire) #replaced ax with fig

        label_y_top = cls.ROW_HEIGHT * 0.8
        label_y_bottom = -(n_rows - 1) * cls.ROW_HEIGHT - cls.ROW_HEIGHT * 0.8
        cls._draw_moment_labels(fig, layout, col_x, label_y_top, label_y_bottom)

        cls._draw_elements(fig, layout, col_x)

        footer_lines = cls._build_footer_lines(layout)
        if footer_lines:
            cls._draw_footer(fig, footer_lines, left_wire, label_y_bottom)

        cls._configure_axes(fig, left_wire, right_wire, label_y_top, label_y_bottom, footer_lines)
        # fig.tight_layout()
        return fig

    @classmethod
    def _draw_qubit_wires(
        cls, fig: go.Figure, layout: CircuitLayout, left_wire: float, right_wire: float
    ) -> None:
        '''
        A CircuitLayout is a Data Structure consisting of:
            Integer -> num_qubits
            Integer -> num_moments
            Listof strings -> qubit_labels
            Listof Strings -> moment_labels
            Listof ??? -> elements
            Float OR None -> global_phase
            ListofStrings -> additional_result_types
            ListofStrings -> unassigned_parameters

        _draw_qubit_wires: PlotlyFigure + CircuitLayout + Float + Float -> None
        plots the qubit wires

        ax.plot args: [x values] [y values] [color][linewidth][zorder]
        Note: zorder is the "stacking order of plot elements". Like the higher the value, the more the image is on top of another (like an overlay)
        # so it this case it'd make more sense for the wires to be at a low order

        '''
        for row_idx, label in enumerate(layout.qubit_labels):
            y_value = -row_idx * cls.ROW_HEIGHT
            fig.add_trace(
                go.Scatter(
                    x=[left_wire, right_wire],
                    y=[y_value,y_value],
                    mode='lines',
                    line=dict(
                        color=cls.WIRE_COLOR,
                        width=cls.WIRE_LW
                    ),
                    zorder=1,
                    showlegend=False,
                    hoverinfo="skip"
                )
            )
            # ax.plot(
            #     [left_wire, right_wire],
            #     [y, y],
            #     color=cls.WIRE_COLOR,
            #     lw=cls.WIRE_LW,
            #     zorder=1,
            # )

            fig.add_annotation(
                x = left_wire - 0.15, # look more into  if it's necessary to multiply by 96
                y = y_value,
                xref = "x",
                yref = "y",
                text = f"{label} :",
                showarrow=False,
                xanchor="right",
                yanchor="middle",
                font=dict(
                    size=cls.QUBIT_LABEL_FONT_SIZE,
                    family="monospace")
            )

            # ax.text(
            #     left_wire - 0.15,
            #     y,
            #     f"{label} :",
            #     ha="right",
            #     va="center",
            #     fontsize=cls.QUBIT_LABEL_FONT_SIZE,
            #     fontfamily="monospace",
            # )

    @classmethod
    def _draw_moment_labels(
        cls,
        fig: go.Figure,
        layout: CircuitLayout,
        col_x: list[float],
        label_y_top: float,
        label_y_bottom: float,
    ) -> None:
        
        """
        A CircuitLayout is a Data Structure consisting of:
            Integer -> num_qubits
            Integer -> num_moments
            Listof strings -> qubit_labels
            Listof Strings -> moment_labels
            Listof ??? -> elements
            Float OR None -> global_phase
            ListofStrings -> additional_result_types
            ListofStrings -> unassigned_parameters

        _draw_moment_labels: PlotlyFigure + CircuitLayout + ListofFloats + Float + Float -> None
        Updates the Plotly Figure by utilizing the data from Circult Layout to draw labels given the parameters for column coords, y-top coords, and y-bottom coords
        """
        moment_col_ranges: list[tuple[str, int, int]] = []
        for col_idx, label in enumerate(layout.moment_labels):
            if moment_col_ranges and moment_col_ranges[-1][0] == label:
                moment_col_ranges[-1] = (label, moment_col_ranges[-1][1], col_idx)
            else:
                moment_col_ranges.append((label, col_idx, col_idx))

        for label, col_start, col_end in moment_col_ranges:
            cx = (col_x[col_start] + col_x[col_end]) / 2
            for y_pos in (label_y_top, label_y_bottom):
                fig.add_annotation(
                x = cx, # look more into  if it's necessary to multiply by 96
                y = y_pos,
                xref = "x",
                yref = "y",
                text = label,
                showarrow=False,
                xanchor="center",
                yanchor="middle",
                font=dict(
                    size=cls.MOMENT_LABEL_FONT_SIZE,
                    family="monospace",
                    color="#555555")
                )
                # ax.text(
                #     cx,
                #     y_pos,
                #     label,
                #     ha="center",
                #     va="center",
                #     fontsize=cls.MOMENT_LABEL_FONT_SIZE,
                #     fontfamily="monospace",
                #     color="#555555",
                # )

    @classmethod
    def _draw_elements(cls, fig: go.Figure, layout: CircuitLayout, col_x: list[float]) -> None:
        """
        A CircuitLayout is a Data Structure consisting of:
            Integer -> num_qubits
            Integer -> num_moments
            Listof strings -> qubit_labels
            Listof Strings -> moment_labels
            Listof [GateBox OR ControlDot OR SwapMarker OR Connection OR BarrierMaker] -> elements, it has to be a list of multiple of these data structures
                fix: used following gate below as example
                Hadamard: {'col': 0, 'label': 'H', 'row': 2} <- GateBox: Number String Number
                CNOT: {'col': 1, 'filled': True, 'row': 0} <- ControlDot: Number Boolean Number
                CNOT: {'col': 1, 'filled': True, 'row': 1} <- ControlDot
                CNOT: {'col': 1, 'label': 'X', 'row': 2} <- GateBox
                CNOT: {'col': 1, 'row_end': 2, 'row_start': 0} <- Connection: Number Number Number
                Hadamard: {'col': 2, 'label': 'H', 'row': 2} <- GateBox
                SWAP: {'col': 3, 'row': 1} <- SwapMarker: Number Number
                SWAP: {'col': 3, 'row': 2} <- SwapMarker
                SWAP: {'col': 3, 'row_end':2, 'row_start':2} <- Connection
                Barrier: {'col': 4, 'row': 1} <- BarrierMaker: Number Number, still trying to figure out how that works
            Float OR None -> global_phase
            ListofStrings -> additional_result_types
            ListofStrings -> unassigned_parameters

        _draw_elements: PlotlyCircuitDiagram + PlotlyFigure + CircuitLayout + ListofFloats -> None
        Given the CircuitLayout.element's data, this method updates the PlotlyFigure by drawing elements while spacing them out with col_x
        It calls other methods depending on the DataType of layout.elements
        IF GateBox -> _draw_gate_box
        IF ControlDot -> _draw_control_dot
        IF SwapMarker -> _draw_swap_marker
        IF Connection -> _draw_connection
        IF BarrierMaker -> _draw_barrier

        Again, we'll have to replace the axes from matplotlib with the PlotlyFigure

        For hover interactivity, need to build a dictionary of controls by column
        Example: Column 1 has controls on rows 0 and 1
        """
        col_controls = {}

        for elem in layout.elements:
            if isinstance(elem, ControlDot):
                if elem.col not in col_controls:
                    col_controls[elem.col] = []
                col_controls[elem.col].append(elem.row)

        for elem in layout.elements:
            if isinstance(elem, GateBox):
                # asses control directly in new GateBox method
                col_controls_temp = col_controls.get(elem.col, None)
                cls._draw_gate_box(fig, elem, col_x[elem.col], control_qubits=col_controls_temp)
            
            elif isinstance(elem, ControlDot):
                cls._draw_control_dot(fig, elem, col_x[elem.col])
            
            elif isinstance(elem, SwapMarker):
                cls._draw_swap_marker(fig, elem, col_x[elem.col])
            
            elif isinstance(elem, Connection):
                cls._draw_connection(fig, elem, col_x[elem.col])
            
            elif isinstance(elem, BarrierMarker):
                cls._draw_barrier(fig, elem, col_x[elem.col])

    @classmethod
    def _build_footer_lines(cls, layout: CircuitLayout) -> list[str]:
        """
        _build_footer_lines: PlotlyCircuitDiagram + CircuitLayout -> Listof String

        This aggregates out a list of additional global phases, result types, or unassigned parameters and sets it as the footer of the diagram

        Most likely will not make changes...?
        """
        footer_lines: list[str] = []
        if layout.global_phase:
            footer_lines.append(f"Global phase: {layout.global_phase}")
        if layout.additional_result_types:
            footer_lines.append(
                f"Additional result types: {', '.join(layout.additional_result_types)}"
            )
        if layout.unassigned_parameters:
            footer_lines.append(f"Unassigned parameters: {', '.join(layout.unassigned_parameters)}")
        return footer_lines

    @classmethod
    def _draw_footer(
        cls, fig: go.Figure, footer_lines: list[str], left_wire: float, label_y_bottom: float
    ) -> None:
        """
        _draw_footer: PlotlyCircuitDiagram + ListofStrings + Float + Float -> None
        Takes the list of additional parameters from _build_footer_lines and illustrates them in a diagram
        """
        footer_y = label_y_bottom - cls.ROW_HEIGHT * 0.7
        for i, line in enumerate(footer_lines):
            fig.add_annotation(
                x = left_wire, # look more into  if it's necessary to multiply by 96
                y = footer_y - i * cls.ROW_HEIGHT * 0.5,
                xref = "x",
                yref = "y",
                text = line,
                showarrow=False,
                xanchor="left",
                yanchor="top",
                font=dict(
                    size=cls.FOOTER_FONT_SIZE,
                    family="monospace",
                    color="#333333")
                )
            # ax.text(
            #     left_wire,
            #     footer_y - i * cls.ROW_HEIGHT * 0.5,
            #     line,
            #     ha="left",
            #     va="top",
            #     fontsize=cls.FOOTER_FONT_SIZE,
            #     fontfamily="monospace",
            #     color="#333333",
            # )

    @classmethod
    def _configure_axes(
        cls,
        fig: go.Figure,
        left_wire: float,
        right_wire: float,
        label_y_top: float,
        label_y_bottom: float,
        footer_lines: list[str],
    ) -> None:
        """
        _configure_axes: PlotlyFigure + Float + Float + Float + Float + ListofStrings -> None
        Based off of the list of parameters from _build_footer_lines, we update the PlotlyFigure by optimizing the axes
        to set the start and end of the x-axis y-axis to ensure that all wires are seen*

        * don't think I'm right on this...
        """
        fig.update_xaxes(
            range=[left_wire - 1.5, right_wire + 0.5],
            visible=False
        )

        y_top = label_y_top + 0.4
        y_bottom = label_y_bottom - 0.4
        if footer_lines:
            y_bottom -= len(footer_lines) * cls.ROW_HEIGHT * 0.5
        
        #ax.set_xlim(left_wire - 1.5, right_wire + 0.5)
        fig.update_yaxes(
            range=[y_bottom, y_top],
            autorange=False,
            visible=False
        )
        # ax.set_ylim(y_bottom, y_top)
        # ax.set_aspect("equal")
        # ax.axis("off")

    @classmethod
    def _draw_gate_box(cls, fig: go.Figure, elem: GateBox, x: float, control_qubits=None) -> None:
        """
        _draw_gate_box: PlotlyCircuitDiagram + PlotlyFigure + GateBox + Float -> None

        Updates PlotlyFigure by drawing the GateBox at x-coordinate

        matplotlib.patches.FancyBboxPatch creates a "box" with the following arguments:
            xy: (float, float) <- lower left corner of bounding box
            width: float <- width of box
            height: float <- height of box
            boxstyle: String <- "round" or "square" or "circle"
            facecolor: String <- fill color
            edgecolor: String <- border color
            linewidth: Number <- border thickness
            zorder: Number <- Overlay priority, higher it is, the more it'll overlay
        
        ALL (I think?) arguments for Plotly's fig.add_shape():
            type: String <- shape type, like 'rect', 'circle', 'line', or 'path'
            x0: Number <- start x-coordinate for the shape
            y0: Number <- start y-coord for the shape
            x1: Number <- ending x-coord
            y1: Number <- ending y-coord
            path: String <- path string for svg file (ONLY if type = path)

            fillcolor: String <- interior color of shape
            opacity: Number <- opacity of shape btwn 0 and 1
            fillrule: String <- How interior of "path" is filled ('evenodd' or 'nonzero')
            line: Dictionary of the following <- shape's outline
                color: String <- color of outline
                width: Number <- width of outline in pixels
                dash: String <- dash style ('solid', 'dot', 'dash', 'longdash', 'dashdot', 'longdashdot')
            
            label: Dictionary of the following <- text labels
                text: String <- String value displaying
                font: Dictionary <- describing font styling
                    color, family, size, weight, textcase, variant
                padding: Number <- internal padding distance in pixels from edge of shape
        """

        
        y = -elem.row * cls.ROW_HEIGHT
        print(f"Drawing box at x={x}, y={y}")
        box_width = cls._gate_box_width(elem.label)

        fig.add_shape(
            xref="x",
            yref="y",
            type="rect", # I see that there are round corners for matplotlib. we can write a custom svg path string to draw out the round outlines, but I don't know how...
            x0=x - box_width / 2,
            y0=y - cls.GATE_BOX_HEIGHT / 2,
            x1=(x - box_width / 2) + box_width,
            y1=(y - cls.GATE_BOX_HEIGHT / 2) + cls.GATE_BOX_HEIGHT,
            fillcolor=cls.GATE_FILL_COLOR,
            line=dict(
                color = cls.GATE_EDGE_COLOR,
                width = 1.2
            ),
            layer='above',
            label=dict(
                text=elem.label,
                textposition='middle center',
                font = dict(
                    size=cls.GATE_FONT_SIZE,
                    family="monospace",
                    color=cls.GATE_TEXT_COLOR,
                )
            )

        )

        fig.update_xaxes(visible=False)
        fig.update_yaxes(
            visible=False,
            scaleanchor="x",
            autorange="reversed"
        )
        
        hover_string = cls._draw_gate_hover_text(elem, control_qubits=control_qubits)
        cls._draw_hover_box(fig, x - box_width / 2, y - cls.GATE_BOX_HEIGHT / 2, 
        (x - box_width / 2) + box_width, (y - cls.GATE_BOX_HEIGHT / 2) + cls.GATE_BOX_HEIGHT, hover_string)

        # rect = mpatches.FancyBboxPatch(
        #     (x - box_width / 2, y - cls.GATE_BOX_HEIGHT / 2),
        #     box_width,
        #     cls.GATE_BOX_HEIGHT,
        #     boxstyle=mpatches.BoxStyle.Round(pad=0.05),
        #     facecolor=cls.GATE_FILL_COLOR,
        #     edgecolor=cls.GATE_EDGE_COLOR,
        #     linewidth=1.2,
        #     zorder=3,
        # )
        # ax.add_patch(rect)
        # ax.text(
        #     x,
        #     y,
        #     elem.label,
        #     ha="center",
        #     va="center",
        #     fontsize=cls.GATE_FONT_SIZE,
        #     fontfamily="monospace",
        #     color=cls.GATE_TEXT_COLOR,
        #     zorder=4,
        # )

    @classmethod
    def _draw_control_dot(cls, fig: go.Figure, elem: ControlDot, x: float) -> None:
        """
        plt.Circle():
            (Float, Float): (x,y) <- center coords of circle
            Float: radius <- radius of circle
            String: color <- edge + face color of circle
            Number: zorder <- overlay priority

        ALL (I think?) arguments for Plotly's fig.add_shape():
            type: String <- shape type, like 'rect', 'circle', 'line', or 'path' REQUIRED
            x0: Number <- start x-coordinate for the shape REQUIRED
            y0: Number <- start y-coord for the shape REQUIRED
            x1: Number <- ending x-coord REQUIRED
            y1: Number <- ending y-coord REQUIRED
            path: String <- path string for svg file (ONLY if type = path)

            don't forgoet xref, yref, and layer!

            fillcolor: String <- interior color of shape
            opacity: Number <- opacity of shape btwn 0 and 1
            fillrule: String <- How interior of "path" is filled ('evenodd' or 'nonzero')
            line: Dictionary of the following <- shape's outline
                color: String <- color of outline
                width: Number <- width of outline in pixels
                dash: String <- dash style ('solid', 'dot', 'dash', 'longdash', 'dashdot', 'longdashdot')
            
            label: Dictionary of the following <- text labels
                text: String <- String value displaying
                font: Dictionary <- describing font styling
                    color, family, size, weight, textcase, variant
                padding: Number <- internal padding distance in pixels from edge of shape

        _draw_control_dot: PlotlyCircuitDiagram + PlotlyFigure + ControlDot + Float -> None
        Updates PlotlyFigure by taking data from ControlDot to draw a dot and apply it on the diagram
        
        quick note on the circle creation
        Matplotlib takes in the center coordinate, whereas Plotly takes in the botomleft coordinates and the topright coordinates
        Since it's the ratio is 1:1 like a square, we can do for example

        Center: (0,0) radius 5
        bottom left: (0 - 5, 0 - 5)
        top right (0 + 5, 0 + 5)

        so bottom left is (x - r, y - r)
        top right is (x + r, y + r)

        """

        y = -elem.row * cls.ROW_HEIGHT

        print(f"Drawing dot  at x={x}, y={y}")
        if elem.filled:
            # circle = plt.Circle(
            #     (x, y),
            #     cls.CONTROL_DOT_RADIUS,
            #     color=cls.CONTROL_DOT_COLOR,
            #     zorder=4,
            # )

            fig.add_shape(
            xref="x",
            yref="y",
            type="circle",
            x0=x - cls.CONTROL_DOT_RADIUS,
            y0=y - cls.CONTROL_DOT_RADIUS,
            x1=x + cls.CONTROL_DOT_RADIUS,
            y1=y + cls.CONTROL_DOT_RADIUS,
            fillcolor=cls.CONTROL_DOT_COLOR,
            layer='above',
            )
        else:
            fig.add_shape(
            xref="x",
            yref="y",
            type="circle",
            x0=x - cls.CONTROL_DOT_RADIUS,
            y0=y - cls.CONTROL_DOT_RADIUS,
            x1=x + cls.CONTROL_DOT_RADIUS,
            y1=y + cls.CONTROL_DOT_RADIUS,
            fillcolor="white",
            layer='above',
            line=dict(
                color=cls.CONTROL_DOT_COLOR,
                width=1.5
                )
            )
            # circle = plt.Circle(
            #     (x, y),
            #     cls.CONTROL_DOT_RADIUS,
            #     facecolor="white",
            #     edgecolor=cls.CONTROL_DOT_COLOR,
            #     linewidth=1.5,
            #     zorder=4,
            # )
        # ax.add_patch(circle)

    @classmethod
    def _draw_swap_marker(cls, fig: go.Figure, elem: SwapMarker, x: float) -> None:

        """
        _draw_swap_marker: PlotlyCircuitDiagram + PlotlyFigure + SwapMarker + Float -> None
        Updates PlotlyFigure by drawing an "x" given the coordinates from PlotlyFigure

        ax.plot arguments:
        x <- x center coords
        y <- y center coords
        "x" <- marker
        markersize <0 controls size of cross
        color <- color of the marker
        markeredgewidth <- thickness of the marker

        quick note: so instead of adding a figure, we can add a trace instead since it takes in a center coordinate too


        """
        y = -elem.row * cls.ROW_HEIGHT
        print(f"Drawing x at x={x}, y={y}")
        fig.add_trace(
            go.Scatter(
                x=[x],
                y=[y],
                mode='markers',
                marker=dict(
                    symbol='x',
                    size=cls.SWAP_MARKER_SIZE,
                    color=cls.CONNECTION_COLOR,
                    line=dict(
                    width=2
                    )
                ),
                zorder= 4
            )
        )

        # ax.plot(
        #     x,
        #     y,
        #     "x",
        #     markersize=cls.SWAP_MARKER_SIZE,
        #     color=cls.CONNECTION_COLOR,
        #     markeredgewidth=2,
        #     zorder=4,
        # )

    @classmethod
    def _draw_connection(cls, fig: go.Figure, elem: Connection, x: float) -> None:
        y_start = -elem.row_start * cls.ROW_HEIGHT
        y_end = -elem.row_end * cls.ROW_HEIGHT
        print(f"Drawing gate at x={x}, y={y_start} to {y_end}")
        fig.add_shape(
            xref="x",
            yref="y",
            type="line",
            x0=x,
            y0=y_start,
            x1=x,
            y1=y_end,
            line=dict(
                width=cls.CONNECTION_LW,
                color=cls.CONNECTION_COLOR,
                dash="solid"
            ),
            layer='below'
            )
        
        # ax.plot(
        #     [x, x],
        #     [y_start, y_end],
        #     color=cls.CONNECTION_COLOR,
        #     lw=cls.CONNECTION_LW,
        #     zorder=2,
        # )

    @classmethod
    def _draw_barrier(cls, fig: go.Figure, elem: BarrierMarker, x: float) -> None:
        """Draw a barrier marker on a single qubit wire.

        Rendered as a small hatched rectangle centered on the qubit wire.
        One marker per targeted qubit; qubits not in the barrier's target
        get no marker.
        """
        y = -elem.row * cls.ROW_HEIGHT

        print(f"Drawing barrier at x={x}, y={y}")
        half_h = cls.ROW_HEIGHT * cls.BARRIER_HEIGHT_FRAC / 2
        half_w = cls.BARRIER_WIDTH / 2

        fig.add_shape(
            xref="x",
            yref="y",
            type="rect",
            x0=x - half_w,
            y0=y- half_h,
            x1=(x - half_w) + cls.BARRIER_WIDTH,
            y1=(y- half_h) + (half_h * 2),
            fillcolor=cls.BARRIER_FILL_COLOR,
            line=dict(
                color = cls.BARRIER_COLOR,
                width = cls.BARRIER_LW
            ),
            layer='above',
            fillpattern=dict(
                shape=cls.BARRIER_HATCH,
                fgcolor=cls.BARRIER_COLOR # hatch lines will match border of barrier
            )
        )

        # rect = mpatches.Rectangle(
        #     (x - half_w, y - half_h),
        #     cls.BARRIER_WIDTH,
        #     half_h * 2,
        #     facecolor=cls.BARRIER_FILL_COLOR,
        #     edgecolor=cls.BARRIER_COLOR,
        #     hatch=cls.BARRIER_HATCH,
        #     linewidth=cls.BARRIER_LW,
        #     zorder=2,
        # )
        # ax.add_patch(rect)
    
    @classmethod
    def _draw_hover_box(cls, fig, x0, y0, x1, y1, hover_text) -> None:
        """Draws a transparent go.Scatter polygon to act as a hover trigger over a GateBox."""
        fig.add_trace(
            go.Scatter(
                x=[x0, x1, x1, x0, x0], # bottom-left, bottom-right, top-right, top-left
                y=[y0, y0, y1, y1, y0],
                mode="lines",
                fill="toself",
                fillcolor="rgba(0,0,0,0)", #transparent
                line=dict(color="rgba(0,0,0,0)"),
                hoveron="fills",
                text=hover_text,
                name="",
                hovertemplate="%{hovertext}<extra></extra>",
                showlegend=False,
                hoverlabel=dict(
                    bgcolor="white",
                    font_size=12,
                    font_family="monospace"
                ),
                zorder=10
            )
        )

    @classmethod
    def _draw_gate_hover_text(cls, element, control_qubits=None, device_metadata=None):
        """
        _build_gate_hover_text: PlotlyCircuitDiagram + GateBox + Dictionary of Properties (optional)
         Extracts gate properties and formats them into an HTML string for Plotly tooltips.

         first identify the gate name
         next figure out the targets and controls (if any)
         then start building the string + its parametrs (if any)
        """
        print(f"DEBUG - Gate: {getattr(element, 'label', 'Unknown')}, Controls: {control_qubits}, Type: {type(control_qubits)}")
        raw_name = str(getattr(element, "label", "Unknown"))

        gate_name = raw_name
        params_str = ""

        if "(" in raw_name and ")" in raw_name:
            gate_name = raw_name.split("(")[0].strip()
            params_str = raw_name.split("(")[1].replace(")", "").strip()

        target_qubit = getattr(element, "row", "Unknown")
        target_str = f"q{target_qubit}"
        
        # Control Gate conditions
        if control_qubits:
            if not gate_name.upper().startswith("C"):
                if len(gate_name) == 1:
                    gate_name = f"C{gate_name.upper()}"
                else:
                    gate_name = f"C{gate_name}"

        hover_html = f"<b>Gate:</b> {gate_name}<br>" # html string
        hover_html += f"<b>Target(s):</b> {target_str}<br>"
        
        # IF gate has parameter (for e.g. rotational gates like rx + ry + rz -> provide the angle or additional parameters?)
        if params_str:
            hover_html += f"<br><b>Gate Parameter/s:</b> {params_str}"

        if device_metadata:
            hover_html += "<br><br><i>Additional Device Information:</i><br>"
            for key, value in device_metadata.items():
                hover_html += f"<b>{key.capitalize()}:</b> {value}<br>"

        return hover_html