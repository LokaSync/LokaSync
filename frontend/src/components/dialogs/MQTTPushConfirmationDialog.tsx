import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Wifi, AlertTriangle, ExternalLink } from "lucide-react";

interface MQTTPushConfirmationDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onConfirm: () => void;
  nodeCodename: string;
  firmwareVersion: string;
  firmwareUrl: string;
  isConnected: boolean;
}

export function MQTTPushConfirmationDialog({
  open,
  onOpenChange,
  onConfirm,
  nodeCodename,
  firmwareVersion,
  firmwareUrl,
  isConnected,
}: MQTTPushConfirmationDialogProps) {
  const handleConfirm = () => {
    onConfirm();
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="w-[95vw] max-w-lg max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-base">
            <Wifi className="h-4 w-4" />
            MQTT Firmware Push
          </DialogTitle>
          <DialogDescription className="text-sm">
            You are about to send firmware update command to{" "}
            <strong className="break-all">{nodeCodename}</strong>
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {/* Firmware Details */}
          <div className="space-y-3">
            <div className="space-y-3 text-sm">
              <div className="flex flex-col gap-1">
                <span className="font-medium text-xs text-muted-foreground">
                  Node:
                </span>
                <span className="font-mono text-xs break-all bg-muted p-2 rounded">
                  {nodeCodename}
                </span>
              </div>

              <div className="flex flex-col gap-1">
                <span className="font-medium text-xs text-muted-foreground">
                  Firmware Version:
                </span>
                <div>
                  <Badge variant="outline" className="text-xs">
                    {firmwareVersion}
                  </Badge>
                </div>
              </div>

              <div className="flex flex-col gap-1">
                <span className="font-medium text-xs text-muted-foreground">
                  Firmware URL:
                </span>
                <div className="bg-muted p-2 rounded">
                  <a
                    href={firmwareUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:text-blue-800 underline text-xs break-all inline-flex items-start gap-1 group"
                  >
                    <span className="break-all">{firmwareUrl}</span>
                    <ExternalLink className="h-3 w-3 flex-shrink-0 mt-0.5 opacity-70 group-hover:opacity-100 transition-opacity" />
                  </a>
                </div>
              </div>
            </div>
          </div>

          <Separator />

          {/* Key Notes */}
          <div className="space-y-3">
            <h4 className="font-medium text-sm flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 text-orange-500" />
              Important Notes:
            </h4>

            <div className="text-xs space-y-2 text-muted-foreground">
              <div className="flex gap-2">
                <span className="font-medium min-w-4">1.</span>
                <span>
                  Ensure the firmware URL you want to upload is accessible.
                </span>
              </div>
              <div className="flex gap-2">
                <span className="font-medium min-w-4">2.</span>
                <span>
                  Verify that constant values like{" "}
                  <code className="bg-muted px-1 rounded text-xs">
                    node_codename
                  </code>
                  ,{" "}
                  <code className="bg-muted px-1 rounded text-xs">
                    firmware_version
                  </code>
                  , and{" "}
                  <code className="bg-muted px-1 rounded text-xs">
                    firmware_url
                  </code>{" "}
                  are correct.
                </span>
              </div>
            </div>
          </div>

          <Separator />

          {/* Warning Alert */}
          <Alert variant="destructive">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription className="text-xs">
              <strong>Warning:</strong>
              <p className="mt-1">
                If there are errors in your firmware and it has already been
                published, this is not a program error, but a{" "}
                <strong className="font-semibold">
                  developer (human) error
                </strong>
                . You or other team members at the node location must perform
                manual reflashing!
              </p>
            </AlertDescription>
          </Alert>
        </div>

        {/* Footer with buttons */}
        <div className="flex gap-3 pt-4">
          <Button
            type="button"
            variant="outline"
            onClick={() => onOpenChange(false)}
            className="flex-1"
          >
            Cancel
          </Button>
          <Button
            onClick={handleConfirm}
            disabled={!isConnected}
            className="bg-blue-600 hover:bg-blue-700 flex-1"
          >
            Send Firmware Update
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
