import * as Scripting from 'resource:///org/gnome/shell/ui/scripting.js';
import Gio from 'gi://Gio';
import GLib from 'gi://GLib';
import Shell from 'gi://Shell';
export const METRICS = {};
export async function run() {
    const root='/home/surface/native-test-results';
    const name=GLib.getenv('SPX_CASE');
    for(const stage of ['static-ready','stress-ready']) {
        let ready=false;
        for(let i=0;i<150;i++) {
            try {
                const [,bytes]=Gio.File.new_for_path(`${root}/${name}-status.json`).load_contents(null);
                if(JSON.parse(new TextDecoder().decode(bytes)).stage===stage) {ready=true;break;}
            } catch(e) {}
            await Scripting.sleep(250);
        }
        if(!ready) {console.error(`SPX_STAGE_TIMEOUT ${stage}`); return;}
        await Scripting.sleep(300);
        const file=Gio.File.new_for_path(`${root}/${name}-${stage}.png`);
        const stream=file.replace(null,false,Gio.FileCreateFlags.REPLACE_DESTINATION,null);
        const pending=new Shell.Screenshot().screenshot(false,stream);
        global.stage.queue_redraw();
        await pending;
        stream.close(null);
        console.log(`SPX_SCREENSHOT ${stage}`);
    }
    const file=Gio.File.new_for_path(`${root}/${name}-capture.done`);
    file.replace_contents('done',null,false,Gio.FileCreateFlags.REPLACE_DESTINATION,null);
    await Scripting.sleep(90000);
}
