import datetime
import logging
import os
import pprint
import time
import shutil

import plotly
import plotly.graph_objs as go

from jinja2 import Environment, PackageLoader, select_autoescape

logger = logging.getLogger(__name__)


class BlockchainPlotter:

    def __init__(self, plot_dir, plot_auto_open):
        self.data_series = []
        if not os.path.isdir(plot_dir):
            os.makedirs(plot_dir)
        self.plot_dir = os.path.realpath(plot_dir)
        self.plot_auto_open = plot_auto_open

        # clear plot directory, create folder for block detail pages and copy .css files into it
        current_dir = os.path.dirname(os.path.abspath(__file__))
        for root, dirs, files in os.walk(plot_dir, topdown=False):
            for f in files:
                to_delete = os.path.join(root, f)
                os.remove(to_delete)
            for dir in dirs:
                os.rmdir(os.path.join(root, dir))
        # TODO time.sleep dirty fix
        time.sleep(1)
        os.mkdir(os.path.join(plot_dir, 'block_detail_pages'))
        shutil.copy(os.path.join(current_dir, 'plot_resources', 'bootstrap.min.css'),
                    os.path.join(plot_dir, 'block_detail_pages', 'bootstrap.min.css'))

    def plot_blockchain(self, event_data):
        logger.debug('Plotting blockchain into dir {}'.format(self.plot_dir))
        # only print if more blocks than the genesis block are present
        if len(event_data['block_chain']._blockchain) > 1:
            self.__generate_plot(event_data['block_chain'])

    @staticmethod
    def __block_label(block):
        return '# {}: {}'.format(block.block_id, block.block_creator_id)

    def __generate_plot(self, blockchain):
        head_hashes = blockchain._current_branch_heads

        my_head_hash = blockchain._node_branch_head
        my_branch = blockchain.get_block_range(range_end=my_head_hash)
        other_branches = [blockchain.get_block_range(range_end=block_hash)
                          for block_hash in head_hashes if block_hash != my_head_hash]
        all_branches = [my_branch] + other_branches
        already_visited = {}

        edge_trace = go.Scatter(
            x=[],
            y=[],
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines')

        node_trace = go.Scatter(
            x=[],
            y=[],
            text=[],
            mode='markers',
            hoverinfo='text')

        branch_number = 0
        for branch in all_branches:
            if branch_number == 0:
                branch_name = 'My Branch'
            else:
                branch_name = 'Branch #{}'.format(branch_number)
            # get blocks in pairs (0,1), (1,2) etc
            # note that the branches are in reverse order so the last block is in branch[0]
            for block, previous_block in self.__pairwise(branch):
                current_block_hash = block.get_computed_hash()
                if current_block_hash in already_visited:
                    break
                else:
                    already_visited[current_block_hash] = branch_name
                if block.predecessor_hash in already_visited:
                    previous_block_branch_name = already_visited[block.predecessor_hash]
                else:
                    previous_block_branch_name = branch_name

                x1, y1 = self.__timestamp_to_datetime(block.timestamp), branch_name

                # draw block
                node_trace['x'].append(x1)
                node_trace['y'].append(y1)
                block_text = pprint.pformat(block.to_dict()).replace("\n", '<br>')
                node_trace['text'].append(block_text)

                if previous_block:
                    x0, y0 = self.__timestamp_to_datetime(previous_block.timestamp), previous_block_branch_name
                    # draw edge
                    edge_trace['x'] += [x0, x1, None]
                    edge_trace['y'] += [y0, y1, None]

                    if previous_block.block_id == 1:
                        # draw first visible block because the loop ends here
                        node_trace['x'].append(x0)
                        node_trace['y'].append(y0)
                        block_text = pprint.pformat(previous_block.to_dict()).replace("\n", '<br>')
                        node_trace['text'].append(block_text)

            branch_number += 1

        snapshot_figure = go.Figure(data=[edge_trace, node_trace],
                                    layout=go.Layout(
                                        title='Blockchain state at {} from node {}'.format(
                                            self.__get_formatted_datetime(),
                                            blockchain._node_id),
                                        titlefont=dict(size=16),
                                        showlegend=False,
                                        hovermode='closest',
                                        # margin=dict(b=20, l=5, r=5, t=40),
                                        annotations=[],
                                        xaxis=dict(showgrid=False,
                                                   zeroline=False,
                                                   showticklabels=True),
                                        yaxis=dict(showgrid=False,
                                                   zeroline=False,
                                                   showticklabels=True,
                                                   type="category",
                                                   autorange=True,
                                                   categoryorder="category descending")))
        plotly.offline.plot(snapshot_figure, filename=os.path.join(self.plot_dir, '{}.html'.format(time.time())),
                            auto_open=self.plot_auto_open)

        self.data_series.append({'data': [edge_trace, node_trace]})
        greatest_range = [min(node_trace['x']), max(node_trace['x'])]
        animated_figure = go.Figure(data=self.data_series[0]['data'],
                                    layout=go.Layout(
                                        title='Animated Blockchain state at {} from node {}'.format(
                                            self.__get_formatted_datetime(),
                                            blockchain._node_id),
                                        titlefont=dict(size=16),
                                        updatemenus=[{'type': 'buttons',
                                                      'buttons': [{'label': 'Play',
                                                                   'method': 'animate',
                                                                   'args': [None]},
                                                                  {'label': 'Pause',
                                                                   'method': 'animate',
                                                                   'args': [[None], {
                                                                       'frame': {'duration': 0, 'redraw': False},
                                                                       'mode': 'immediate',
                                                                       'transition': {'duration': 0}}]},
                                                                  ]},
                                                     ],
                                        showlegend=False,
                                        hovermode='closest',
                                        # margin=dict(b=20, l=5, r=5, t=40),
                                        annotations=[],
                                        xaxis=dict(showgrid=False,
                                                   zeroline=False,
                                                   showticklabels=True,
                                                   range=greatest_range,
                                                   autorange=False
                                                   ),
                                        yaxis=dict(showgrid=False,
                                                   zeroline=False,
                                                   showticklabels=True,
                                                   type="category",
                                                   autorange=True,
                                                   categoryorder="category descending")),
                                    frames=go.Frames(self.data_series))
        plotly.offline.plot(animated_figure, filename=os.path.join(self.plot_dir, 'animated.html'),
                            auto_open=False)

    def generate_block_detail_page(self, event_data):
        block = event_data['block']
        env = Environment(
            loader=PackageLoader('labchain', 'plot_resources'),
            autoescape=select_autoescape(['html', 'xml'])
        )
        block_hash = block.get_computed_hash()
        template_data = block.to_dict()
        template_data['block_hash'] = block_hash
        template_data['transactions'] = []
        for transaction in block.transactions:
            template_data['transactions'].append(transaction.to_dict())

        # used for jinja2
        if len(template_data['transactions']) == 0:
            template_data['transactions'] = None

        template = env.get_template('block_detail_template.html')
        rendered_html = template.render(template_data)
        f = open(os.path.join(self.plot_dir, 'block_detail_pages', str(block.block_id) + '.html'), 'w')
        f.write(rendered_html)
        f.close()

    @staticmethod
    def __get_formatted_datetime():
        return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    @staticmethod
    def __timestamp_to_datetime(timestamp):
        # this is necessary for windows
        if timestamp < 86400:
            timestamp = 86400
        return datetime.datetime.fromtimestamp(timestamp)

    @staticmethod
    def __pairwise(iterable):
        "s -> (s0,s1), (s1,s2), (s2, s3), ..."
        if len(iterable) == 1:
            return [(iterable[0], None)]
        return zip(iterable[:-1], iterable[1:])
