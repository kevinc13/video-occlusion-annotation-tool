var fs   = require('fs');
    util = require('util');
    mime = require('mime');
    path = require('path');

function base64Img(src) {
    var data = fs.readFileSync(src).toString('base64');
    return util.format('data:%s;base64,%s', mime.getType(src), data);
}

/*
 *    Possible argument positions
 *
 *    converter frameStart(number) frameEnd(number) folder(string) outputFile(string)
 *    converter folder(string) outputFile(string)
 *
 */

if(process.argv.length > 2) {
    // Check if the first argument is a number or string
    if(!isNaN(parseInt(process.argv[2]))) {
        var frameStart = process.argv[2],
            frameEnd = process.argv[3],
            frameIncrement = process.argv[4]
            folder = process.argv[5],
            outputFile = process.argv[6],
            dataUri = null,
            framesImg = [];
    } else {
        var frameStart = 1,
            frameEnd = fs.readdirSync(process.argv[2]).length,
            folder = process.argv[2],
            outputFile = process.argv[3];
    }

    var dataUri = null,
        framesImg = [],
        files = fs.readdirSync(folder)

    for (let file of files) {
      console.log('Converting file: ' + file)
      dataUri = base64Img(folder + file)
      framesImg.push(dataUri)
    }
    // for (; frameStart <= frameEnd; frameStart += frameIncrement) {
    //     console.log('Converting file: ' + frameStart);
    //     dataUri = base64Img(folder + frameStart + fileTypeExt);
    //     framesImg[frameStart] = dataUri;
    // }

    framesImg.splice(null, 1);

    var json = {
        frames: framesImg
    };

    fs.writeFile(outputFile, JSON.stringify(json), function(err) {
        if(err) {
            console.log(err);
        } else {
            console.log('Completed!');
        }
    });
} else {
    console.error('Not enough parameters supplied!');
}
