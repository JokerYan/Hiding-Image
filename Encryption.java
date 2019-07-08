import java.awt.image.BufferedImage;
import java.io.*;
import java.util.*;

import javax.imageio.ImageIO;

public class Encryption{
    static BufferedImage baseImage, targetImage, outputImage;
    static int targetHeight, targetWidth, decryptedHeight, decryptedWidth;
    static int order, total;
    static int serialBlockSize = 4, reserveSize = 8;
    public static void main(String[] args) {
        try{
            baseImage = ImageIO.read(new File("base.jpg"));
            targetImage = ImageIO.read(new File("icon.jpg"));
        } catch(IOException e){
            System.err.println("Image not exist");
            System.exit(-1);
        }
        targetHeight = targetImage.getHeight();
        targetWidth = targetImage.getWidth();

        total = 1;
        while(total < 256){
            order += 1;
            total *= serialBlockSize;
        }

        int[] baseImgArr = getImageArray(baseImage);
        int[] targetImgArr = getImageArray(targetImage);
        prepareBaseImage(baseImgArr);
        int[] serial = serializeImage(targetImgArr);
        int[] combinedImgArr = combineImage(baseImgArr, serial);
        reconstructImage(combinedImgArr, baseImage.getWidth(), baseImage.getHeight(), "combined.jpg");

        int[] decryptedSerial = separateImage(combinedImgArr);
        int[] decryptedImgArr = deserializeImage(decryptedSerial);
        reconstructImage(decryptedImgArr, decryptedWidth, decryptedHeight, "result.jpg");
        return;
    }

    private static void prepareBaseImage(int[] baseImgArr){
        for(int i = 0; i < baseImgArr.length; i++){
            baseImgArr[i] = baseImgArr[i] & 0xfcfcfc;
        }
    }

    private static int[] serializeImage(int[] targetImgArr){
        int length = targetImgArr.length * 3 * order;
        int[] result = new int[length];
        for(int i = 0; i < targetImgArr.length; i++){
            int b = targetImgArr[i] & 0xff;
            int g = (targetImgArr[i] & 0xff00) >> 8;
            int r = (targetImgArr[i] & 0xff0000) >> 16;
            int[] bArray = convertBase(b, serialBlockSize, true);
            int[] gArray = convertBase(g, serialBlockSize, true);
            int[] rArray = convertBase(r, serialBlockSize, true);
            for(int j = 0; j < order; j++){
                int pos = (i * order + j) * 3;
                result[pos] = bArray[j];
                result[pos + 1] = gArray[j];
                result[pos + 2] = rArray[j];
            }
        }
        return result;
    }

    private static int[] combineImage(int[] baseImgArr, int[] serial){
        int[] widthSerial = convertBase(targetWidth, serialBlockSize, false);
        int[] heightSerial = convertBase(targetHeight, serialBlockSize, false);

        for(int i = 0; i < reserveSize; i++){
            baseImgArr[i] += widthSerial[i];
            baseImgArr[i + reserveSize] += heightSerial[i];
        }

        for(int i = 0; i < serial.length; i++){
            int offset = i % 3;
            int pos = i / 3 + reserveSize * 2;
            baseImgArr[pos] += serial[i] << (8 * offset);
        }

        return baseImgArr;
    }

    private static int[] separateImage(int[] combinedImgArr){
        int[] widthArr = new int[reserveSize];
        int[] heightArr = new int[reserveSize];
        for(int i = 0; i < reserveSize; i++){
            widthArr[i] = combinedImgArr[i] & 0x3;
            heightArr[i] = combinedImgArr[i + reserveSize] & 0x3;
        }

        int width = reverseBase(widthArr, serialBlockSize);
        int height = reverseBase(heightArr, serialBlockSize);
        decryptedWidth = width;
        decryptedHeight = height;
        int[] serial = new int[width * height * 3 * order];

        for(int i = 0; i < width * height * order; i++){
            int pixel = combinedImgArr[i + reserveSize * 2];
            serial[i * 3] = combinedImgArr[i + reserveSize * 2] & 0x3;
            serial[i * 3 + 1] = (combinedImgArr[i + reserveSize * 2] & 0x300) >> 8;
            serial[i * 3 + 2] = (combinedImgArr[i + reserveSize * 2] & 0x30000) >> 16;
        }

        return serial;
    }

    private static int[] deserializeImage(int[] serial){
        int width = decryptedWidth;
        int height = decryptedHeight;
        int[] result = new int[width * height];
        for(int i = 0; i < width * height; i++){
            int[] bArr = new int[order];
            int[] gArr = new int[order];
            int[] rArr = new int[order];
            for(int j = 0; j < order; j++){
                int pos = i * 3 * order + j * 3;
                bArr[j] = serial[pos];
                gArr[j] = serial[pos + 1];
                rArr[j] = serial[pos + 2];
            }
            result[i] += reverseBase(bArr, serialBlockSize);
            result[i] += reverseBase(gArr, serialBlockSize) << 8;
            result[i] += reverseBase(rArr, serialBlockSize) << 16;

            result[i] |= 0xff << (3 * 8);
        }
        return result;
    }

    private static void reconstructImage(int[] imageArray, int width, int height, String name){
        BufferedImage result = new BufferedImage(width, height, BufferedImage.TYPE_3BYTE_BGR);
        result.setRGB(0, 0, width, height, imageArray, 0, width);
        try{
            ImageIO.write(result, "JPEG", new File(name));
        }catch(IOException e){
            System.err.println("Error writing image");
            System.exit(-1);
        }
    }

    private static int[] convertBase(int num, int base, boolean short_mode){
        int length;
        if(short_mode){
            length = order;
        }else{
            length = reserveSize;
        }

        int[] result = new int[length];
        int index = length - 1;
        while(num > 0){
            result[index--] = num % base;
            num = num / base;
        }

        return result;
    }

    private static int reverseBase(int[] array, int base){
        int result = 0;
        for (int digit : array) {
            result = result * base + digit;
        }
        return result;
    }

    private static int[] getImageArray(BufferedImage img){
        int[] result = new int[img.getHeight() * img.getWidth()];
        img.getRGB(0, 0, img.getWidth(), img.getHeight(), result, 0, img.getWidth());
        return result;
    }
}