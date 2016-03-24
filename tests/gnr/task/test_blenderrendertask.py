import unittest
import os
from random import randrange, shuffle

from PIL import Image

from gnr.task.blenderrendertask import BlenderDefaults, BlenderRenderTask, PreviewUpdater


class TestBlenderDefaults(unittest.TestCase):
    def test_init(self):
        bd = BlenderDefaults()
        self.assertTrue(os.path.isfile(bd.main_program_file))

class TestBlenderTaskDivision(unittest.TestCase):
    program_file = "example_program_file"
    open(program_file, 'w').close()
    bt = BlenderRenderTask(
                 node_name = "example-node-name",
                 task_id = "example-task-id",
                 main_scene_dir = os.getcwd(),
                 main_scene_file = "example.blend",
                 main_program_file = program_file,
                 total_tasks = 7,
                 res_x = 200,
                 res_y = 300,
                 outfilebasename = "example_out",
                 output_file = "",
                 output_format = "PNG",
                 full_task_timeout = 1,
                 subtask_timeout = 1,
                 task_resources = [],
                 estimated_memory = 123,
                 root_path = os.getcwd(),
                 use_frames = False,
                 frames = [1],
                 engine = "CYCLES"
                 )
    
    def test_blender_task(self):
        self.assertIsInstance(self.bt, BlenderRenderTask)
        self.assertTrue(self.bt.main_scene_file == "example.blend")

    def test_get_min_max_y(self):
        self.assertTrue(self.bt.res_x == 200)
        self.assertTrue(self.bt.res_y == 300)
        self.assertTrue(self.bt.total_tasks == 7)
        for tasks in [1, 6, 7, 20, 60]:
            self.bt.total_tasks = tasks
            for yres in range(100, 1000):
                self.bt.res_y = yres
                cur_max_y = self.bt.res_y
                for i in range(1, self.bt.total_tasks + 1):
                    min_y, max_y = self.bt._get_min_max_y(i)
                    min_y = int(float(self.bt.res_y) * (min_y))
                    max_y = int(float(self.bt.res_y) * (max_y)) 
                    self.assertTrue(max_y == cur_max_y)
                    cur_max_y = min_y
                self.assertTrue(cur_max_y == 0)
        
        
class TestPreviewUpdater(unittest.TestCase):
    def test_update_preview(self):
        preview_file = os.path.join(os.getcwd(), 'sample_img.png')
        res_x = 200
        
        for chunks in range (1, 100):
            res_y = 0
            expected_offsets = {}
            chunks_sizes = {}
            for i in range (1, chunks + 1): #subtask numbers start from 1
                y = randrange(1, 100)
                expected_offsets[i] = res_y
                chunks_sizes[i] = y
                res_y += y
            pu = PreviewUpdater(preview_file, res_x, res_y, expected_offsets)
            chunks_list = range (1, chunks + 1)
            shuffle(chunks_list)
            chunks_files = {}
            for i in chunks_list:
                img = Image.new("RGB", (res_x, chunks_sizes[i]))
                file1 = os.path.join(os.getcwd(), 'chunk{}.png'.format(i))
                img.save(file1)
                chunks_files[i] = file1
                pu.update_preview(file1, i)
            for f in chunks_files:
                os.remove(chunks_files[f])
            self.assertTrue(pu.perfect_match_area_y == res_y and pu.perfectly_placed_subtasks == chunks)
                