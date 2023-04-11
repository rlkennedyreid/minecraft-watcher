workflow control-vm {

    # Input parameters for runbook
    Param(
        [string]$resourceGroup,
        [string]$VM,
        [string]$action
    )

    # Ensures you do not inherit an AzContext in your runbook
    Disable-AzContextAutosave -Scope Process

    # Connect to Azure with system-assigned managed identity
    Connect-AzAccount -Identity

    # Start or stop VM
    if ($action -eq "Start") {
        Start-AzVM -Name $VM -ResourceGroupName $resourceGroup -DefaultProfile $AzureContext
    }
    elseif ($action -eq "Stop") {
        Stop-AzVM -Name $VM -ResourceGroupName $resourceGroup -DefaultProfile $AzureContext -Force
    }
    else {
        Write-Output "`r`n Action not allowed. Please enter 'stop' or 'start'."
    }
}
