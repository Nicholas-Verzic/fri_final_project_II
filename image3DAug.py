import json
import glob
from PIL import Image, ImageDraw
import math
import copy
import open3d as o3d
import matplotlib.pyplot as plt
import numpy as np
import cv2 as cv


def lastChar(s, c):
    return -(s[::-1].index(c) + 1)

def pause():
    while True:
        print("running")


class PerspectiveTransform:
    transformedIMG = None

    # {
    #     "shape_attributes": {
    #         "name": "ellipse",
    #         "cx": 2326,
    #         "cy": 1172,
    #         "rx": 108.738,
    #         "ry": 115.355,
    #         "theta": -2.664
    #     },
    #     "region_attributes": {
    #         "Classification": "Label"
    #     }
    # },

    def ellipseTransform(self, x, y, angle, ellipseRegions):
        for i in range(len(ellipseRegions)):
            soh = math.sin(ellipseRegions[i]["shape_attributes"]["theta"])
            cah = math.cos(ellipseRegions[i]["shape_attributes"]["theta"])
            (cy, cx) = self.transformedPoint(
                x,
                y,
                angle,
                ellipseRegions[i]["shape_attributes"]["cy"],
                ellipseRegions[i]["shape_attributes"]["cx"],
            )
            ellipseRegions[i]["shape_attributes"]["rx"] = math.dist(
                self.transformedPoint(
                    x,
                    y,
                    angle,
                    ellipseRegions[i]["shape_attributes"]["cy"]
                    + (soh * ellipseRegions[i]["shape_attributes"]["rx"]),
                    ellipseRegions[i]["shape_attributes"]["cx"]
                    + (cah * ellipseRegions[i]["shape_attributes"]["rx"]),
                ),
                (cy, cx),
            )
            ellipseRegions[i]["shape_attributes"]["ry"] = math.dist(
                self.transformedPoint(
                    x,
                    y,
                    angle,
                    ellipseRegions[i]["shape_attributes"]["cy"]
                    + (cah * ellipseRegions[i]["shape_attributes"]["ry"]),
                    ellipseRegions[i]["shape_attributes"]["cx"]
                    + (soh * ellipseRegions[i]["shape_attributes"]["ry"]),
                ),
                (cy, cx),
            )
            (
                ellipseRegions[i]["shape_attributes"]["cy"],
                ellipseRegions[i]["shape_attributes"]["cx"],
            ) = (cy, cx)

            self.draw.line((ellipseRegions[i]["shape_attributes"]["cx"] + (cah * ellipseRegions[i]["shape_attributes"]["rx"]), ellipseRegions[i]["shape_attributes"]["cy"] + (soh * ellipseRegions[i]["shape_attributes"]["rx"]), ellipseRegions[i]["shape_attributes"]["cx"] - (cah * ellipseRegions[i]["shape_attributes"]["ry"]), ellipseRegions[i]["shape_attributes"]["cy"] - (soh * ellipseRegions[i]["shape_attributes"]["ry"])), width = 3)
            self.draw.line((ellipseRegions[i]["shape_attributes"]["cx"] + (soh * ellipseRegions[i]["shape_attributes"]["rx"]), ellipseRegions[i]["shape_attributes"]["cy"] + (cah * ellipseRegions[i]["shape_attributes"]["rx"]), ellipseRegions[i]["shape_attributes"]["cx"] - (soh * ellipseRegions[i]["shape_attributes"]["ry"]), ellipseRegions[i]["shape_attributes"]["cy"] - (cah * ellipseRegions[i]["shape_attributes"]["ry"])), width = 3)

        # print(ellipseRegions)
        return ellipseRegions

    # {
    #     "shape_attributes": {
    #         "name": "circle",
    #         "cx": 2569,
    #         "cy": 2790,
    #         "r": 82.503
    #     },
    #     "region_attributes": {
    #         "Type": "Button"
    #     }
    # },

    def circleTransform(self, x, y, angle, circleRegions):
        for i in range(len(circleRegions)):
            circleRegions[i]["shape_attributes"]["name"] = "ellipse"
            (cy, cx) = self.transformedPoint(
                x,
                y,
                angle,
                circleRegions[i]["shape_attributes"]["cy"],
                circleRegions[i]["shape_attributes"]["cx"],
            )
            circleRegions[i]["shape_attributes"]["rx"] = (
                self.transformedPoint(
                    x,
                    y,
                    angle,
                    circleRegions[i]["shape_attributes"]["cy"],
                    circleRegions[i]["shape_attributes"]["cx"]
                    + circleRegions[i]["shape_attributes"]["r"],
                )[1]
                - cx
            )
            circleRegions[i]["shape_attributes"]["ry"] = (
                self.transformedPoint(
                    x,
                    y,
                    angle,
                    circleRegions[i]["shape_attributes"]["cy"]
                    + circleRegions[i]["shape_attributes"]["r"],
                    circleRegions[i]["shape_attributes"]["cx"],
                )[0]
                - cy
            )
            (
                circleRegions[i]["shape_attributes"]["cy"],
                circleRegions[i]["shape_attributes"]["cx"],
            ) = (cy, cx)
            circleRegions[i]["shape_attributes"].pop("r")
            circleRegions[i]["shape_attributes"]["theta"] = 0

            self.draw.line((circleRegions[i]["shape_attributes"]["cx"] - circleRegions[i]["shape_attributes"]["rx"], circleRegions[i]["shape_attributes"]["cy"], circleRegions[i]["shape_attributes"]["cx"] + circleRegions[i]["shape_attributes"]["rx"], circleRegions[i]["shape_attributes"]["cy"]), width = 3)
            self.draw.line((circleRegions[i]["shape_attributes"]["cx"], circleRegions[i]["shape_attributes"]["cy"] - circleRegions[i]["shape_attributes"]["ry"], circleRegions[i]["shape_attributes"]["cx"], circleRegions[i]["shape_attributes"]["cy"] + circleRegions[i]["shape_attributes"]["ry"]), width = 3)

        # print(circleRegions)
        return circleRegions

    # {
    #     "shape_attributes": {
    #         "name": "polygon",
    #         "all_points_x": [
    #             1565,
    #             1438,
    #             1439,
    #             1563
    #         ],
    #         "all_points_y": [
    #             2651,
    #             2651,
    #             2768,
    #             2769
    #         ]
    #     },
    #     "region_attributes": {
    #         "Type": "button"
    #     }
    # },

    # {
    #     "shape_attributes": {
    #         "name": "polyline",
    #         "all_points_x": [
    #             2232,
    #             2223,
    #             2434,
    #             2437,
    #             2232
    #         ],
    #         "all_points_y": [
    #             2677,
    #             2879,
    #             2888,
    #             2684,
    #             2675
    #         ]
    #     },
    #     "region_attributes": {
    #         "Type": "Label"
    #     }
    # },

    def polyTransform(self, x, y, angle, polyRegions):
        for i in range(len(polyRegions)):
            for j in range(len(polyRegions[i]["shape_attributes"]["all_points_x"])):
                (
                    polyRegions[i]["shape_attributes"]["all_points_y"][j],
                    polyRegions[i]["shape_attributes"]["all_points_x"][j],
                ) = self.transformedPoint(
                    x,
                    y,
                    angle,
                    polyRegions[i]["shape_attributes"]["all_points_y"][j],
                    polyRegions[i]["shape_attributes"]["all_points_x"][j],
                )

                if j > 0:
                    self.draw.line((polyRegions[i]["shape_attributes"]["all_points_x"][j-1], polyRegions[i]["shape_attributes"]["all_points_y"][j-1], polyRegions[i]["shape_attributes"]["all_points_x"][j], polyRegions[i]["shape_attributes"]["all_points_y"][j]), width = 3)

        # print(polyRegions)
        return polyRegions

    # {
    #     "shape_attributes": {
    #         "name": "rect",
    #         "x": 1362,
    #         "y": 2038,
    #         "width": 86,
    #         "height": 84
    #     },
    #     "region_attributes": {
    #         "Type": "label"
    #     }
    # },

    def rectTransform(self, x, y, angle, rectRegions):
        for i in range(len(rectRegions)):
            rectRegions[i]["shape_attributes"]["name"] = "polygon"

            pointList = []

            pointList.append(
                self.transformedPoint(
                    x,
                    y,
                    angle,
                    rectRegions[i]["shape_attributes"]["y"],
                    rectRegions[i]["shape_attributes"]["x"],
                )
            )
            pointList.append(
                self.transformedPoint(
                    x,
                    y,
                    angle,
                    rectRegions[i]["shape_attributes"]["y"]
                    + rectRegions[i]["shape_attributes"]["height"],
                    rectRegions[i]["shape_attributes"]["x"]
                    + rectRegions[i]["shape_attributes"]["width"],
                )
            )
            pointList.append(
                self.transformedPoint(
                    x,
                    y,
                    angle,
                    rectRegions[i]["shape_attributes"]["y"],
                    rectRegions[i]["shape_attributes"]["x"]
                    + rectRegions[i]["shape_attributes"]["width"],
                )
            )
            pointList.append(
                self.transformedPoint(
                    x,
                    y,
                    angle,
                    rectRegions[i]["shape_attributes"]["y"]
                    + rectRegions[i]["shape_attributes"]["height"],
                    rectRegions[i]["shape_attributes"]["x"],
                )
            )

            rectRegions[i]["shape_attributes"].pop("x")
            rectRegions[i]["shape_attributes"].pop("y")
            rectRegions[i]["shape_attributes"].pop("width")
            rectRegions[i]["shape_attributes"].pop("height")

            rectRegions[i]["shape_attributes"]["all_points_x"] = [i[1] for i in pointList]
            rectRegions[i]["shape_attributes"]["all_points_y"] = [i[0] for i in pointList]

            for j in range(len(rectRegions[i]["shape_attributes"]["all_points_x"])):
                if j > 0:
                    self.draw.line((rectRegions[i]["shape_attributes"]["all_points_x"][j-1], rectRegions[i]["shape_attributes"]["all_points_y"][j-1], rectRegions[i]["shape_attributes"]["all_points_x"][j], rectRegions[i]["shape_attributes"]["all_points_y"][j]), width = 3)

        # print(rectRegions)
        return rectRegions

    def __init__(self, angles, fillColor=(0)):
        self.angles = angles
        self.fillColor = fillColor

    def __call__(self, val, path, imgName, tIm, H, W, cam, parCap):
        jsonArr = []
        y = H
        x = W

        circleRegions = []
        polyRegions = []
        ellipseRegions = []
        rectRegions = []

        # print("\n\n\nRegioning")
        for region in val["regions"]:
            if region["shape_attributes"]["name"] == "rect":
                rectRegions.append(region)
            elif region["shape_attributes"]["name"] == "ellipse":
                ellipseRegions.append(region)
            elif region["shape_attributes"]["name"] == "circle":
                circleRegions.append(region)
            elif (
                region["shape_attributes"]["name"] == "polyline"
                or region["shape_attributes"]["name"] == "polygon"
            ):
                polyRegions.append(region)
        # print("Done Regioning\n\n\n")

        # print(rectRegions)
        # print(ellipseRegions)
        # print(circleRegions)
        # print(polyRegions)

        for i, angle in enumerate(self.angles):
            print(str(i + 2) + key)
            try:
                image = copy.deepcopy(tIm)
                value = copy.deepcopy(val)

                value["filename"] = str(i + 2) + imgName

                R = image.get_rotation_matrix_from_xyz((0, math.radians(angle), 0))
                image.rotate(R, center=(0, 0, 0))

                # image = image.crop(o3d.geometry.AxisAlignedBoundingBox(min_bound=(-int(H/2), -int(W/2), -H), max_bound=(int(H/2), int(W/2), H)))
                # o3d.visualization.draw_geometries([o3d.geometry.TriangleMesh.create_coordinate_frame(size=100, origin=[0, 0, 0]), image])

                vis.clear_geometries()
                vis.add_geometry(image)
                vis.update_geometry(image)
                vis.add_geometry(o3d.geometry.TriangleMesh.create_coordinate_frame(size=100, origin=[0, 4000, 0]))
                vis.update_geometry(o3d.geometry.TriangleMesh.create_coordinate_frame(size=100, origin=[0, 4000, 0]))
                cam.convert_from_pinhole_camera_parameters(parCap, allow_arbitrary=True)
                # cam.camera_local_translate(W/10, 0, 0)
                vis.poll_events()
                vis.update_renderer()

                tempIm = vis.capture_screen_float_buffer()

                npIm = np.array(tempIm) * 255
                gray = cv.cvtColor(npIm, cv.COLOR_RGB2GRAY)
                gray = (255 - gray)
                npIm = cv.cvtColor(npIm, cv.COLOR_BGR2RGB)
                
                thresh = cv.threshold(gray.astype('uint8'), 1, 255, cv.THRESH_BINARY)[1]
                kernel = np.ones((5, 5), np.uint8)
                thresh = cv.erode(thresh, kernel, iterations=1)
                contours, _ = cv.findContours(image=thresh, mode=cv.RETR_TREE, method=cv.CHAIN_APPROX_SIMPLE)
                areas = [cv.contourArea(contour) for contour in contours]
                contArea = areas.index(max(areas))
                contours = tuple(cv.approxPolyDP(contours[contArea], 30, True))

                # cv.drawContours(image=thresh, contours=contours, contourIdx=-1, color=(150), thickness=5)
                # cv.imshow("Temp", thresh)
                # cv.waitKey()

                xVals = [coords[0][0] for coords in contours]
                yVals = [coords[0][1] for coords in contours]
                xVals.sort()
                yVals.sort()

                minY = int((yVals[1]+yVals[0])/2)
                maxY = int((yVals[-1]+yVals[-2])/2)

                _, xShape, _ = npIm.shape
                xWidth = int((maxY-minY)*H/(2*W))
                npIm = npIm[minY:maxY+1, int((xShape/2)-xWidth):int((xShape/2)+xWidth)]
                
                npIm = cv.resize(npIm, (H, W))
                cv.imwrite(path + value["filename"], npIm)

                self.transformedIMG = image

                self.draw = ImageDraw.Draw(self.tIMG)

                newShape = []

                print("Rect Transform")
                newShape = newShape + self.rectTransform(x, y, angle, copy.deepcopy(rectRegions))
                print("Ellipse Transform")
                newShape = newShape + self.ellipseTransform(
                    x, y, angle, copy.deepcopy(ellipseRegions)
                )
                print("Circle Transform")
                newShape = newShape + self.circleTransform(
                    x, y, angle, copy.deepcopy(circleRegions)
                )
                print("Poly Transform")
                newShape = newShape + self.polyTransform(x, y, angle, copy.deepcopy(polyRegions))
                value["regions"] = newShape

                jsonArr.append(value)

                # self.tIMG.show()
                # self.draw = None

                vis.clear_geometries()

            except Exception as e:
                print(e)
        # print(jsonArr)
        return jsonArr


if __name__ == "__main__":
    buildingDirectories = glob.glob("./*/")

    vis = o3d.visualization.Visualizer()
    vis.create_window(visible=True)
    cam = vis.get_view_control()

    # vis.set_full_screen(True)

    # vis.add_geometry(o3d.geometry.TriangleMesh.create_coordinate_frame(size=100, origin=[0, 0, 0]))
    # vis.update_geometry(o3d.geometry.TriangleMesh.create_coordinate_frame(size=100, origin=[0, 0, 0]))

    for path in buildingDirectories:
        pictures = glob.glob(path + "*.jpg")
        jsonFile = glob.glob(path + "*.json")
        transformer = PerspectiveTransform([-30, -15, 15, 30])
        if len(jsonFile) > 0:
            with open(jsonFile[0], "r") as read_file:
                data = copy.deepcopy(json.load(read_file))
                picJSON = data["_via_img_metadata"]
                z = 0
                for pic in pictures:
                    # print(np.zeros_like(cv2.imread(pic)[:, :, 0]).shape)
                    tempPic = np.ones_like(cv.imread(pic)[:, :, 0]).transpose()
                    print(tempPic.shape)
                    # print(tempPic.shape)
                    print(np.ascontiguousarray(tempPic).astype(np.float32).shape)
                    depIm = o3d.geometry.Image(np.ascontiguousarray(tempPic).astype(np.float32))
                    colImg = o3d.io.read_image(pic)

                    print(depIm)
                    print(colImg)
                    img = o3d.geometry.RGBDImage.create_from_color_and_depth(colImg, depIm, convert_rgb_to_intensity=False)

                    H, W = tempPic.shape
                    f = 0.001
                    intrinsic = o3d.camera.PinholeCameraIntrinsic(W, H, f, f, 0, 0)
                    rotIm = o3d.geometry.PointCloud.create_from_rgbd_image(img, intrinsic)
                    R = rotIm.get_rotation_matrix_from_xyz((0, math.pi, -math.pi/2))
                    c = rotIm.get_center()
                    rotIm.translate(-c)
                    rotIm.rotate(R, center=(0, 0, 0))

                    # o3d.visualization.draw_geometries([o3d.geometry.TriangleMesh.create_coordinate_frame(size=100, origin=[0, 0, 0]), rotIm])

                    vis.clear_geometries()
                    vis.add_geometry(rotIm)
                    vis.update_geometry(rotIm)

                    cam.camera_local_translate(W/10, 0, 0)
                    vis.poll_events()
                    vis.update_renderer()
                    if z == 0:
                        z = 1
                        parCap = cam.convert_to_pinhole_camera_parameters()

                    tempPic = pic[lastChar(pic, "\\") + 1 :]
                    for key, value in picJSON.items():
                        if tempPic in key:
                            print((value, path, tempPic, rotIm, H, W))
                            print("BREAK")
                            for i, d in enumerate(transformer(value, path, tempPic, rotIm, H, W, cam, parCap)):
                                data["_via_img_metadata"][str(i + 2) + key] = d
                                if data["_via_image_id_list"].count(str(i + 2) + key) == 0:
                                    data["_via_image_id_list"].append(str(i + 2) + key)
                            break

                # print(data)
                with open(jsonFile[0][:-5] + "Revised.json", "w") as newFile:
                    json.dump(data, newFile)
            read_file.close()
    vis.destroy_window()